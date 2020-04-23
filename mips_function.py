import re
from tiger_ir_parser import parseLine, parseJR
from mc_instruction import MCInstruction

class MIPSFunction():
    def __init__(self, lines):
        self.name = self._parseTigerIRFunctionName(lines)
        self.instructions = self._fromTigerIRInstructions(lines)
        self._parseTigerIRLocalArrays(lines)
    
    def _fromTigerIRInstructions(self, lines):
        instructions = []
        # load args
        args = self._parseTigerIRFunctionArgs(lines)
        instructions += self._getArgStackLoads(args)

        # parse instructions
        for line in lines[4:]:
            parsed = parseLine(line)
            instructions += parsed

        # alloc local arrays
        localArrays = self._parseTigerIRLocalArrays(lines)
        for arr in localArrays:
            line = "assign, {}, {}, 0".format(arr.symbol, arr.size)
            instructions = parseLine(line) + instructions
        
        # insert calling convention
        instructions = self._insertCallingConvention(instructions)
        # insert function name label
        instructions.insert(0, MCInstruction('label', target=self.name))
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
    
    # assumes the current stack pointer is offset by 40 (rv + $fp + 8 $s regs) from last arg on stack ($ra not included ion this count)
    def _getArgStackLoads(self, args):
        instructions = []
        for i in range(0, len(args)):
            arg = args[i]
            offset = (len(args) - i) * 4 + 40
            instructions.append(MCInstruction('lw', targetReg=arg, sourceRegs=['$sp'], offset=offset))
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
    
    def _insertCallingConvention(self, instructions):
        newInstructions = instructions[:]
        if self.name != 'main':
            pre_convention = []
            pre_convention += self._getSregSaves()
            pre_convention += self._saveReg('$fp')
            pre_convention += self._saveReg('$ra')
            
            # consider doing reg allocation here

            post_convention = []
            post_convention += self._restoreReg('$ra')
            post_convention += self._restoreReg('$fp')
            post_convention += self._getSregRestores()

            newInstructions = pre_convention + newInstructions + post_convention
            newInstructions = self._processReturn(newInstructions)
        if self.name == 'main':
            newInstructions += self._getSystemExit()
        return newInstructions
    
    def _getSystemExit(self):
        return [
            MCInstruction("li", targetReg="$v0", imm=10),
            MCInstruction("syscall")
        ]

    def _processReturn(self, instructions):
        newInstructions = []
        jrInstructions = None
        for instr in instructions:
            if instr.op == 'jr':
                jrInstructions = parseJR(instr)
            else:
                newInstructions.append(instr)
        if jrInstructions != None:
            newInstructions += jrInstructions
        else:
            newInstructions += [
                MCInstruction('jr', sourceRegs=['$ra'])
            ]
        return newInstructions

    def _getSregSaves(self):
        instructions = []
        imm = 8 * -4
        instructions += [ MCInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=imm), ]
        for i in range(0, 8):
            sreg = '$s' + str(i)
            offset = i*4
            instructions += [
                MCInstruction('sw', targetReg='$sp', sourceRegs=[sreg], offset=offset)
            ]
        return instructions
    
    def _getSregRestores(self):
        instructions = []
        imm = 8 * 4
        instructions += [ MCInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=imm), ]
        for i in range(0, 8):
            sreg = '$s' + str(7-i)
            offset = i*-4
            instructions += [
                MCInstruction('lw', targetReg=sreg, sourceRegs=['$sp'], offset=offset),
            ]
        return instructions
    
    def _saveReg(self, reg):
        return [
            MCInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=-4),
            MCInstruction('sw', targetReg='$sp', sourceRegs=[reg], offset=0)
        ]
    
    def _restoreReg(self, reg):
        return [
            MCInstruction('lw', targetReg=reg, sourceRegs=['$sp'], offset=0),
            MCInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=4)
        ]

class MIPSFunctionArg():
    def __init__(self, symbol, isArray=False, size=1):
        if (size < 1):
            raise ValueError("arg with symbol {} has size = {} < 1".format(symbol, size))
        if (not isArray) and size != 1:
            raise ValueError("arg with symbol {} is not an array and has size = {} != 1".format(symbol, size))
        
        self.symbol = symbol
        self.isArray = isArray
        self.size = size