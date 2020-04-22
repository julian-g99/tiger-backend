from MIPSFunction import MIPSFunction

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
            return functions

    def _parseTigerIRFunctionDelims(self, lines):
        functions = []
        i = 0
        while i < len(lines):
            # loop until first function delim
            while i < len(lines):
                line = self._stripLine(lines[i])
                print(line)
                if line == '#start_function':
                    function = []
                    # add lines to function until next function delim
                    while (i < len(lines) and (line != '#end_function')):
                        function.append(line)
                        i += 1
                        line = self._stripLine(lines[i])
                    if i < len(lines):
                        function.append(line)
                        i += 1
                    # add function to functions and continue looping
                    functions.append(function)
        return functions
                    
    def _stripLine(self, line):
        return line.strip('\n\t\r ')
    
    def _insertCallingConvention(self):
        if self.functions == None:
            raise ValueError("Cannot process calling convention until functions are defined")
        pass
