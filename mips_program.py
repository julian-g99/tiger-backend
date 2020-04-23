from mips_function import MIPSFunction
from mc_instruction import MCInstruction
from tiger_ir_parser import parseLine
from register_alloc import GreedyMIPSAllocator, NaiveMIPSAllocator
import re

class MIPSProgram():
    def __init__(self, inputTigerIRFile=None):
        if inputTigerIRFile == None:
            raise ValueError("inputTigerIRFile cannot be None")
        self.functions = self._fromTigerIRFile(inputTigerIRFile)
    
    def _fromTigerIRFile(self, fname, alloc='greedy'):
        with open(fname, 'r') as fp:
            # group lines into functions
            lines = fp.readlines()
            groups = self._parseTigerIRFunctionDelims(lines)

            # convert groups into list of MIPSFunction objects
            functions = []
            for group in groups:
                functions.append(MIPSFunction(group))
            return functions
    
    def _writeToSFile(self, fname):
        with open(fname, 'w') as fp:
            for func in self.functions:
                for instr in func.instructions:
                    fp.writelines(str(instr) + '\n')

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
    
    def _insertCallingConvention(self, functions, alloc='greedy'):
        # find main function
        for func in functions:
            convention = []
            if func.name == 'main':
                # perform register allocation for main. No calling convention required
                convention = self._regAlloc(func.instructions, allocType=alloc)
                convention += self._getSystemExit()
            else:
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
                line = None
                endOffset = 0
                if len(func.instructions) > 0:
                    i = 0
                    line = func.instructions[i]
                    convention.append(line)
                    # calculate endOffset and add instructions along the way
                    while (i < len(func.instructions)) and type(line) != str: # return instructions are left as str to be parsed after calling convention
                        i += 1
                        if i < len(func.instructions):
                            line = func.instructions[i]
                            convention.append(line)
                    if i < len(func.instructions):
                        # don't keep the found return list
                        convention.pop()
                        endOffset = (len(func.instructions) - i - 1) * -1
                    # append rest of instructions
                    i += 1
                    while (i < len(func.instructions)):
                        line = func.instructions[i]
                        convention.append(line)
                        i += 1
                
                # perform register allocation
                convention = self._regAlloc(convention, allocType=alloc)

                # inc stack by 1
                convention.insert(endOffset, self._getStackPop(1))
                # load $ra from the stack
                convention.insert(endOffset, self._getRegLoad('$ra'))
                convention.insert(endOffset, self._getStackPop(1))
                # load all 8 $s regs from the stack
                for j in range(0, 8):
                    sreg = '$s' + str(7-j)
                    convention.insert(endOffset, self._getRegLoad(sreg))
                    convention.insert(endOffset, self._getStackPop(1))
                # insert function name label
            convention = parseLine("{}:".format(func.name)) + convention
            convention = self._stackResetCleanUp(convention)
            func.instructions = convention

    def _regAlloc(self, instructions, allocType='greedy'):
        allocator = None
        if allocType == 'greedy':
            allocator = GreedyMIPSAllocator(instructions)
        elif allocType == 'naive':
            allocator = NaiveMIPSAllocator(instructions)
        else:
            allocator = GreedyMIPSAllocator(instructions)
        target = re.compile(r'@[a-zA-Z_][a-zA-z0-9]*')
        return allocator.allocInstructions(target=target, physical='$t', regex=True, auto_spill=None)
    
    # fixes a bug where final stackReset from reg allocator is put after the calling convention.
    # This method manually moves that stack reset to before the calling convention so that the calling
    # convention can assume the $sp has not changed.
    def _stackResetCleanUp(self, instructions):
        i = 0
        found = False
        while i < len(instructions) and not found:
            line = str(instructions[i])
            if line == "lw $s7, 0($sp)":
                found = True
            else:
                i += 1
        if found:
            instructions.insert(i-1, instructions[-1])
            return instructions[:-1]
        return instructions

    def _getStackAlloc(self, amount):
        imm = amount * -4
        return MCInstruction('addi', regs=['$sp', '$sp'], imm=imm)
    
    def _getSystemExit(self):
        return [
            MCInstruction('li', regs=['$v0'], imm=10),
            MCInstruction('syscall')
        ]
    
    def _getRegStore(self, reg):
        return MCInstruction('sw', regs=[reg, '$sp'], offset=0)

    def _getRegLoad(self, reg):
        return MCInstruction('lw', regs=[reg, '$sp'], offset=0)

    def _getStackPop(self, amount):
        imm = amount * 4
        return MCInstruction('addi', regs=['$sp', '$sp'], imm=imm)

            
        
