from mips_function import MIPSFunction
from mc_instruction import MCInstruction
from tiger_ir_parser import parseLine, parseReturn

class MIPSProgram():
    def __init__(self, inputTigerIRFile=None):
        if inputTigerIRFile == None:
            raise ValueError("inputTigerIRFile cannot be None")
        self.functions = self._fromTigerIRFile(inputTigerIRFile)
    
    def _fromTigerIRFile(self, fname):
        with open(fname, 'r') as fp:
            # group lines into functions
            lines = fp.readlines()
            groups = self._parseTigerIRFunctionDelims(lines)

            # convert groups into list of MIPSFunction objects
            functions = []
            for group in groups:
                functions.append(MIPSFunction(group))
            self._insertCallingConvention(functions)
            return functions

    def _parseTigerIRFunctionDelims(self, lines):
        functions = []
        i = 0
        while i < len(lines):
            # loop until first function delim
            while i < len(lines):
                line = self._stripLine(lines[i])
                if line == '#start_function':
                    function = []
                    # add lines to function until next function delim
                    while (i < len(lines) and (line != '#end_function')):
                        function.append(line)
                        i += 1
                        line = self._stripLine(lines[i])
                    if i < len(lines):
                        function.append(line)
                    # add function to functions and continue looping
                    functions.append(function)
                i += 1
        return functions
                    
    def _stripLine(self, line):
        return line.strip('\n\t\r ')
    
    def _insertCallingConvention(self, functions):
        # find main function
        for func in functions:
            convention = []
            if func.name != 'main':
                # save all 8 $s regs to the stack
                for i in range(0, 8):
                    convention.append(self._getStackAlloc(1))
                    sreg = '$s' + str(i)
                    convention.append(self._getRegStore(sreg))
                # save $ra to the stack
                convention.append(self._getStackAlloc(1))
                convention.append(self._getRegStore('$ra'))
                # dec stack by 1
                convention.append(self._getStackAlloc(1))
            # loop to end of function or first return
            foundReturn = False
            line = None
            if len(func.instructions) > 0:
                i = 0
                line = func.instructions[i]
                convention.append(line)
                while (i < len(func.instructions)) and type(line) != str: # return instructions are left as str to be parsed after calling convention
                    i += 1
                    if i < len(func.instructions):
                        line = func.instructions[i]
                        convention.append(line)
                if i < len(func.instructions):
                    # don't keep the found return list
                    convention.pop()
                    foundReturn = True
            # inc stack by 1
            convention.append(self._getStackPop(1))
            # load $ra from the stack
            convention.append(self._getRegLoad('$ra'))
            convention.append(self._getStackPop(1))
            # load all 8 $s regs from the stack
            for j in range(0, 8):
                sreg = '$s' + str(7-j)
                convention.append(self._getRegLoad(sreg))
                convention.append(self._getStackPop(1))
            if foundReturn:
                # parse return instruction
                convention += parseReturn(line)
            # insert function name label
            convention = parseLine("{}:".format(func.name)) + convention
            func.instructions = convention


    def _getStackAlloc(self, amount):
        imm = amount * -4
        return MCInstruction('addi', regs=['$sp', '$sp'], imm=imm)
    
    def _getRegStore(self, reg):
        return MCInstruction('sw', regs=[reg, '$sp'], offset=0)

    def _getRegLoad(self, reg):
        return MCInstruction('lw', regs=[reg, '$sp'], offset=0)

    def _getStackPop(self, amount):
        imm = amount * 4
        return MCInstruction('addi', regs=['$sp', '$sp'], imm=imm)

            
        
