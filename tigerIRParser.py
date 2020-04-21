import re

def parseLine(line):
    inType = _getInstructionType(line)