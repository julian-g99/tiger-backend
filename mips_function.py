import re
from tiger_ir_parser import parseLine
from mips_instruction import MIPSInstruction
import register_allocator as ra

class MIPSFunction():
    def __init__(self, lines):
        self.name = self._parseTigerIRFunctionName(lines)
        self.instructions = self._fromTigerIRInstructions(lines)
        self._parseTigerIRLocalArrays(lines)
    
    def _fromTigerIRInstructions(self, lines):
        instructions = []
        # parse instructions
        for line in lines[4:]:
            parsed = parseLine(line)
            instructions += parsed

        # alloc local arrays
        localArrays = self._parseTigerIRLocalArrays(lines)
        for arr in localArrays:
            line = "assign, {}, {}, 0".format(arr.symbol, arr.size)
            instructions = parseLine(line) + instructions
        
        # load args
        args = self._parseTigerIRFunctionArgs(lines)
        instructions = self._getArgStackLoads(args) + instructions

        # allocate physical registers
        instructions = self._getAllocatedPhysicalRegisters(instructions)

        # insert pre calling convention
        self._insertPreCallingConvention(instructions)

        # insert post calling convention
        self._insertPostCallingConvention(instructions)

        # insert function name label
        instructions.insert(0, MIPSInstruction('label', target=self.name))

        return instructions

    def _parseTigerIRFunctionName(self, lines):
        sig = lines[1]
        name = sig.split(" ")[1]
        name = name.split("(")[0]
        return name
    
    def _parseTigerIRFunctionArgs(self, lines):
        args = lines[1]
        args = args.split("(")[1]
        pattern = re.compile(r'int\[[0-9]+\] [a-zA-Z_][a-zA-z0-9_]*')
        pargs = re.findall(pattern, args)
        pattern = re.compile(r'int [a-zA-Z_][a-zA-z0-9_]*')
        pargs += re.findall(pattern, args)
        pargs = [a.split(" ")[1] for a in pargs]
        return pargs
    
    def _getIntListCount(self, lines):
        intList = lines[2]
        ints = intList.split(':')[1]
        if ints == '':
            return 0
        return len(ints.split(','))
    
    def _getArgStackLoads(self, args):
        # params start at ra + rv + oldFp + 8 sregs + 1 = 11 * 4 = 44
        fpParamOffset = 44
        instructions = []
        for i in range(0, len(args)):
            arg = args[i]
            offset = fpParamOffset + (len(args) - i) * 4
            instructions.append(MIPSInstruction('lw', targetReg=arg, sourceRegs=['$fp'], offset=offset))
        return instructions
        
    def _parseTigerIRLocalArrays(self, lines):
        arrayArgs = self._parseTigerIRArrayArgs(lines)
        arrayInts = self._parseTigerIRArrayInts(lines)
        localArrays = []
        for arrInt in arrayInts:
            found = False
            for arrArg in arrayArgs:
                if arrInt.symbol == arrArg.symbol:
                    found = True
            if not found:
                localArrays.append(arrInt)
        return localArrays
        
    def _parseTigerIRArrayArgs(self, lines):
        sig = lines[1]
        pattern = re.compile(r'int\[[0-9]+\] [a-zA-Z_][a-zA-z0-9_]*')
        arrs = re.findall(pattern, sig)
        arrayArgs = []
        for a in arrs:
            size = int(a.split(' ')[0].split('[')[-1][:-1])
            symbol = a.split(' ')[1]
            arrayArgs.append(MIPSFunctionArg(symbol, isArray=True, size=size))
        return arrayArgs

    def _parseTigerIRArrayInts(self, lines):
        ints = lines[2]
        pattern = re.compile(r'[a-zA-Z_][a-zA-z0-9_]*\[[0-9]+\]')
        arrs = re.findall(pattern, ints)
        arrayArgs = []
        for a in arrs:
            size = int(a.split('[')[1][:-1])
            symbol = a.split('[')[0]
            arrayArgs.append(MIPSFunctionArg(symbol, isArray=True, size=size))
        return arrayArgs
    
    def _insertPreCallingConvention(self, instructions):
        if self.name != 'main':
            preConvention = []
            preConvention += self._getSregStores()
            preConvention += self._storeReg('$fp')
            preConvention += self._storeReg('$ra')
            preConvention += [ MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=-4) ] # dec 1 extra space
            preConvention += [ MIPSInstruction('move', targetReg='$fp', sourceRegs=['$sp']) ] # set the new $fp
            i = 0
            for instr in preConvention:
                instructions.insert(i, instr)
                i+=1
        else:
            instructions.insert(0, MIPSInstruction('move', targetReg='$fp', sourceRegs=['$sp'])) # main still needs to set $fp
    
    def _insertPostCallingConvention(self, instructions):
        postConvention = []
        if self.name != 'main':
            postConvention += [ MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=4) ] # inc 1 extra space
            postConvention += self._loadReg('$ra')
            postConvention += self._loadReg('$fp')
            postConvention += self._getSregLoads()
            postConvention += [ MIPSInstruction('jr', sourceRegs=['$ra']) ]
            if instructions[-1].op == 'jr':
                instructions.pop(-1)
        else:
            postConvention += self._getSystemExit()
        for instr in postConvention:
            instructions.append(instr)

    def _getSystemExit(self):
        return [
            MIPSInstruction("li", targetReg="$v0", imm=10),
            MIPSInstruction("syscall")
        ]

    def _getSregStores(self):
        instructions = []
        imm = 8 * -4
        instructions += [ MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=imm), ]
        for i in range(0, 8):
            sreg = '$s' + str(i)
            offset = i*4
            instructions += [
                MIPSInstruction('sw', targetReg='$sp', sourceRegs=[sreg], offset=offset)
            ]
        return instructions
    
    def _getSregLoads(self):
        instructions = []
        imm = 8 * 4
        instructions += [ MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=imm), ]
        for i in range(0, 8):
            sreg = '$s' + str(7-i)
            offset = i*-4
            instructions += [
                MIPSInstruction('lw', targetReg=sreg, sourceRegs=['$sp'], offset=offset),
            ]
        return instructions
    
    def _storeReg(self, reg):
        return [
            MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=-4),
            MIPSInstruction('sw', targetReg='$sp', sourceRegs=[reg], offset=0)
        ]
    
    def _loadReg(self, reg):
        return [
            MIPSInstruction('lw', targetReg=reg, sourceRegs=['$sp'], offset=0),
            MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=4)
        ]

    def _getAllocatedPhysicalRegisters(self, instructions):
        return ra.greedyAlloc(instructions, choke=5)

class MIPSFunctionArg():
    def __init__(self, symbol, isArray=False, size=1):
        if (size < 1):
            raise ValueError("arg with symbol {} has size = {} < 1".format(symbol, size))
        if (not isArray) and size != 1:
            raise ValueError("arg with symbol {} is not an array and has size = {} != 1".format(symbol, size))
        
        self.symbol = symbol
        self.isArray = isArray
        self.size = size