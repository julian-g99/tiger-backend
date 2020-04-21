import re

class MIPSFunction():
    def __init__(self, lines, framePointer=None):
        self.instructions = self._fromTigerIRLines(lines)
        self.framePointer = framePointer
    
    def fromTigerIRLines(self, lines):
        pass

    def _parseTigerIRHeader(self, lines):
        pass

    def _parseTigerIRLocalArrays(self, lines):
        pass
    
    def _parseTigerIRInstructions(self, lines):
        pass

class MIPSFunctionArg():
    def __init__(self, symbol, isArray=False, size=1):
        if (size < 1):
            raise ValueError("arg with symbol {} has size = {} < 1".format(symbol, size))
        if (not isArray) and size != 1:
            raise ValueError("arg with symbol {} is not an array and has size = {} != 1".format(symbol, size))
        
        self.symbol = symbol
        self.isArray = isArray
        self.size = size