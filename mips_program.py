from mips_function import MIPSFunction
from mips_instruction import MIPSInstruction
from tiger_ir_parser import parseLine
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
        
