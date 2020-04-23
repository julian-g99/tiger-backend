import re
from control_flow_graph import BB

mipsPhysicalRegTable = {'$t':10, '$s':8}
virutalRegRegex = re.compile(r'!?[a-zA-Z_][a-zA-Z0-9_]*')


def greedyAlloc(instructions):
    vregs = _parseVirtualRegs(instructions)
    pregs = _getMIPSPhyicicalRegs('$t') # allow for customization later
    regMap = _getAllocationMap(instructions, vregs=vregs, pregs=pregs)
    
    # hot swap
    for i in range(0, len(instructions)):
        _mapInstruction(instructions[i], regMap)

# only supports hot swap
def _mapInstruction(instruction, regMap):
    targetReg = instruction.targetReg
    if targetReg != None:
        if targetReg in regMap.keys():
            instruction.targetReg = regMap[targetReg]
    sourceRegs = instruction.sourceRegs
    if sourceRegs != None:
        for i in range(0, len(sourceRegs)):
            sourceReg = sourceRegs[i]
            if sourceReg in regMap.keys():
                instruction.sourceRegs[i] = regMap[sourceReg]

def _getAllocationMap(instructions, vregs=None, pregs=None):
    if vregs == None:
        vregs = _parseVirtualRegs(instructions)
    if pregs == None:
        symbol = '$t'
        pregs = _getMIPSPhyicicalRegs(symbol)
    liveRanges = _getLiveRanges(instructions)
    sortedVregs = _sortByLiveRangeCardinality(liveRanges)
    regMap = _mapSortedVirtualRegs(sortedVregs, pregs)
    return regMap

# computes the i+ liverange sets 
def _getLiveRanges(instructions, vregs=None):
    if vregs == None:
        vregs = _parseVirtualRegs(instructions)
    
    # init live table
    liveRanges = {}
    for reg in vregs:
        liveRanges[reg] = []
    
    for i in range(len(instructions)-1, -1, -1):
        sourceRegs = instructions[i].sourceRegs
        if sourceRegs != None:
            for reg in sourceRegs:
                if reg in vregs:
                    proposal = []
                    j = i - 1
                    targetReg = instructions[j].targetReg
                    while j >= 0 and targetReg != reg:
                        proposal.append(j)
                        j -= 1
                        targetReg = instructions[j].targetReg
                    if j >= 0:
                        proposal.append(j)
                        _mergeProposal(reg, proposal, liveRanges)

    return liveRanges

# liverange helper method
def _mergeProposal(reg, proposal, liveRanges):
    for pp in proposal:
        if pp not in liveRanges[reg]:
            liveRanges[reg].append(pp)
    
def _sortByLiveRangeCardinality(liveRanges):
    sortedRegs = []
    while len(sortedRegs) < len(liveRanges.keys()):
        maxReg = None
        maxRegCard = None
        for reg in liveRanges.keys():
            if reg not in sortedRegs:
                regCard = len(liveRanges[reg])
                if maxReg == None:
                    maxReg = reg
                    maxRegCard = regCard
                else:
                    if regCard > maxRegCard:
                        maxReg = reg
                        maxRegCard = regCard
        sortedRegs.append(maxReg)
    return sortedRegs

# assigns pregs to the first len(pregs) sortedVregs. All other sortedVregs are spilled
def _mapSortedVirtualRegs(sortedVregs, pregs):
    regMap = {}
    mappedPregs = []
    for i in range(0, len(sortedVregs)):
        vreg = sortedVregs[i]
        if len(mappedPregs) < len(pregs):
            for pr in pregs:
                if pr not in mappedPregs:
                    regMap[vreg] = pr
                    mappedPregs.append(pr)
                    break
        else:
            regMap[vreg] = None
    return regMap

def _parseVirtualRegs(instructions, regex=None):
    if regex == None:
        regex = virutalRegRegex
    vregs = []
    for instr in instructions:
        targetReg = instr.targetReg
        sourceRegs = instr.sourceRegs
        if targetReg != None:
            if re.fullmatch(regex, targetReg) != None and targetReg not in vregs:
                vregs.append(targetReg)
        if sourceRegs != None:
            for reg in sourceRegs:
                if re.fullmatch(regex, reg) != None and reg not in vregs:
                    vregs.append(reg)
    return vregs

def _getMIPSPhyicicalRegs(symbol, customCount=None):
    if symbol in mipsPhysicalRegTable:
        num = mipsPhysicalRegTable[symbol]
        if customCount != None:
            num = customCount
        return _generatePhysicalRegs(symbol, num)
    else:
        raise AllocationException("symbol: {} is not an allocatable MIPS register symbol".format(symbol)) 

def _generatePhysicalRegs(symbol, num):
    return [symbol + str(i) for i in range(0, num)]


class AllocationException(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)



def main():
    regs = _getMIPSPhyicicalRegs("$a", customCount = None)
    print(regs)

if __name__ == "__main__":
    main()