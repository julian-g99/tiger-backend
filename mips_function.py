import re
from tiger_ir_parser import parseLine, parseJR
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

        # process jr instruction
        jrCount = self._processReturn(instructions)

        # allocate physical registers
        argCount = len(args)
        instructions = self._getAllocatedPhysicalRegisters(instructions, argCount=argCount, jrCount=jrCount)

        # insert pre calling convention
        self._insertPreCallingConvention(instructions, argCount=argCount)

        # insert post calling convention
        self._insertPostCallingConvention(instructions, jrCount=jrCount)

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
    
    # assumes the current stack pointer is point at the return value.
    def _getArgStackLoads(self, args):
        instructions = []
        for i in range(0, len(args)):
            arg = args[i]
            offset = (len(args) - i) * 4
            instructions.append(MIPSInstruction('lw', targetReg=arg, sourceRegs=['$sp'], offset=offset))
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
    
    def _insertPreCallingConvention(self, instructions, argCount=0):
        if self.name != 'main':
            preConvention = []
            preConvention += self._getSregSaves()
            preConvention += self._saveReg('$fp')
            preConvention += self._saveReg('$ra')
            i = 0
            for instr in preConvention:
                instructions.insert(argCount+i, instr)
                i+=1
    
    def _insertPostCallingConvention(self, instructions, jrCount=0):
        postConvention = []
        if self.name != 'main':
            postConvention += self._restoreReg('$ra')
            postConvention += self._restoreReg('$fp')
            postConvention += self._getSregRestores()
            for instr in postConvention:
                instructions.insert(-jrCount, instr)

    def _getSystemExit(self):
        return [
            MIPSInstruction("li", targetReg="$v0", imm=10),
            MIPSInstruction("syscall")
        ]

    def _processReturn(self, instructions):
        newInstructions = []
        jrInstructions = None
        for instr in instructions:
            if instr.op == 'jr':
                jrInstructions = parseJR(instr)
            else:
                newInstructions.append(instr)
    
        if jrInstructions == None:
            if self.name == 'main':
                jrInstructions = self._getSystemExit()
            else:
                jrInstructions = [ MIPSInstruction('jr', sourceRegs=['$ra']) ]
                
        
        newInstructions += jrInstructions
        instructions.clear()
        for instr in newInstructions:
            instructions.append(instr)
        return len(jrInstructions)

    def _getSregSaves(self):
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
    
    def _getSregRestores(self):
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
    
    def _saveReg(self, reg):
        return [
            MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=-4),
            MIPSInstruction('sw', targetReg='$sp', sourceRegs=[reg], offset=0)
        ]
    
    def _restoreReg(self, reg):
        return [
            MIPSInstruction('lw', targetReg=reg, sourceRegs=['$sp'], offset=0),
            MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=4)
        ]

    def _getAllocatedPhysicalRegisters(self, instructions, jrCount=0, argCount=0):
        return ra.greedyAlloc(instructions, choke=9, jrCount=jrCount, argCount=argCount)

class MIPSFunctionArg():
    def __init__(self, symbol, isArray=False, size=1):
        if (size < 1):
            raise ValueError("arg with symbol {} has size = {} < 1".format(symbol, size))
        if (not isArray) and size != 1:
            raise ValueError("arg with symbol {} is not an array and has size = {} != 1".format(symbol, size))
        
        self.symbol = symbol
        self.isArray = isArray
        self.size = size