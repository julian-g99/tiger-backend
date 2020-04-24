import re
from control_flow_graph import BB
from mips_instruction import MIPSInstruction

mipsPhysicalRegTable = {'$t':10, '$s':8}
virutalRegRegex = re.compile(r'!?[a-zA-Z_][a-zA-Z0-9_]*')


def greedyAlloc(instructions, argCount=0, choke=None):
    vregs = _parseVirtualRegs(instructions)
    pregs = _getMIPSPhyicicalRegs('$t', customCount=choke) # allow for customization later
    regMap = _getAllocationMap(instructions, vregs=vregs, pregs=pregs)
    print(regMap)

    newInstructions = []
    # setup the frame and load $fp
    frameMap = _getFrameMap(regMap)
    for instruction in instructions:
        newInstructions += _mapInstruction(instruction, regMap, frameMap)
    # _setUnknownOffsets(instructions, len(vregs)) 
    _insertFrameSetup(newInstructions, regMap, argCount=argCount)
    _insertFrameBreakDown(newInstructions, frameMap)
    return newInstructions

# intelligent instruction mapping that handles spilled registers
def _mapInstruction(instruction, regMap, frameMap):
    mappedInstruction = []
    spillMap = _getSpillMap(instruction, regMap)
    # spill
    mappedInstruction += _spillRegs(instruction, spillMap, regMap, frameMap)
    # hot swap
    localRegMap = _getLocalRegMap(spillMap, regMap)
    _hotSwapInstruction(instruction, localRegMap, regMap, spillMap)
    mappedInstruction.append(instruction)
    # mop
    mappedInstruction += _mopRegs(instruction, spillMap, regMap, frameMap)
    
    return mappedInstruction

# unintelligent instruction mapping according to localRegMap
def _hotSwapInstruction(instruction, localRegMap, regMap, spillMap):
    targetReg = instruction.targetReg
    if targetReg != None:
        if targetReg in localRegMap.keys():
            instruction.targetReg = localRegMap[targetReg]
    
    sourceRegs = instruction.sourceRegs
    if sourceRegs != None:
        for i in range(0, len(sourceRegs)):
            sourceReg = sourceRegs[i]
            if sourceReg in localRegMap.keys():
                instruction.sourceRegs[i] = localRegMap[sourceReg]

# this local register map will exclude any spilled registered not specified in the spillMap
def _getLocalRegMap(spillMap, regMap):
    localRegMap = {}
    for reg in regMap.keys():
        if _isMapped(reg, regMap):
            if reg in spillMap.keys():
                localRegMap[reg] = None
                localRegMap[spillMap[reg]] = regMap[reg]
            else:
                localRegMap[reg] = regMap[reg]
    return localRegMap

def _getSpillMap(instruction, regMap):
    spillMap = {}
    targetReg = instruction.targetReg
    sourceRegs = instruction.sourceRegs
    if sourceRegs != None:
        for sourceReg in sourceRegs:
            if sourceReg in regMap.keys() and not _isMapped(sourceReg, regMap):
                if not sourceReg in spillMap.values():
                    victim = _selectSourceRegSpillVictim(instruction, spillMap, regMap)
                    spillMap[victim] = sourceReg
    if targetReg != None and targetReg in regMap.keys():
        if not _isMapped(targetReg, regMap):
            if not targetReg in spillMap.values():
                victim = _selectTargetRegSpillVictim(instruction, spillMap, regMap)
                spillMap[victim] = targetReg
    return spillMap

def _selectTargetRegSpillVictim(instruction, spillMap, regMap):
    # assumes there are atleast 3 available mapped virtual registers to choose from, not apart of this instruction 
    for reg in regMap.keys():
        isMapped = _isMapped(reg, regMap)
        isNotInSourceRegs = (instruction.sourceRegs == None) or (not reg in instruction.sourceRegs)
        isNotVictim = not (reg in spillMap.keys())
        if isMapped and isNotInSourceRegs and isNotVictim:
            return reg
    raise AllocationException("failed to select target reg victim for instruction: {}".format(str(instruction)))

def _selectSourceRegSpillVictim(instruction, spillMap, regMap):
    # assumes there are atleast 3 available mapped virtual registers to choose from, not apart of this instruction 
    for reg in regMap.keys():
        isMapped = _isMapped(reg, regMap)
        isNotInSourceRegs = (instruction.sourceRegs == None) or (not reg in instruction.sourceRegs)
        isNotTargetReg = (instruction.targetReg == None) or (reg != instruction.targetReg)
        isNotVictim = not (reg in spillMap.keys())
        if isMapped and isNotInSourceRegs and isNotTargetReg and isNotVictim:
            return reg
    raise AllocationException("failed to select source reg victim for instruction: {}".format(str(instruction)))

def _isMapped(reg, regMap):
    return regMap[reg] != None

# pre instructions for safely clearing up physical regs for use
def _spillRegs(instruction, spillMap, regMap, frameMap):
    newInstructions = []
    for victim in spillMap.keys():
        incoming = spillMap[victim]
        # optimization if spilled reg is the targetReg and doesnt appear in source regs
        isTargetReg = (instruction.targetReg != None) and (incoming == instruction.targetReg)
        notInSourceRegs = (instruction.sourceRegs == None) or (incoming not in instruction.sourceRegs)
        isNotSW = instruction.op != 'sw'
        if isTargetReg and notInSourceRegs and isNotSW and False:
            # no need to load anything into the target reg so we stash instead of fully swap
            newInstructions += _stashReg(victim, regMap, frameMap)
        else:
            newInstructions += _swapInReg(victim, incoming, regMap, frameMap)
    return newInstructions

# post instructions for safely restoring virtual regs to their original mapped physical regs
def _mopRegs(instruction, spillMap, regMap, frameMap):
    newInstructions = []
    for victim in spillMap.keys():
        outgoing = spillMap[victim]
        newInstructions += _swapOutReg(victim, outgoing, regMap, frameMap)
    return newInstructions

# puts a victim onto the stack and loads the incoming reg into the victim's former physical reg
def _swapInReg(victim, incoming, regMap, frameMap):
    physicalReg = regMap[victim]
    victimOffset = frameMap[victim]
    incomingOffset = frameMap[incoming]
    return [
        MIPSInstruction('sw', targetReg='$fp', sourceRegs=[physicalReg], offset=victimOffset),
        MIPSInstruction('lw', targetReg=physicalReg, sourceRegs=['$fp'], offset=incomingOffset)
    ]

# saves the outgoing reg and returns a victim from the stack back to its original physical register
def _swapOutReg(victim, outgoing, regMap, frameMap):
    physicalReg = regMap[victim]
    victimOffset = frameMap[victim]
    outgoingOffset = frameMap[outgoing]
    return [
        MIPSInstruction('sw', targetReg='$fp', sourceRegs=[physicalReg], offset=outgoingOffset),
        MIPSInstruction('lw', targetReg=physicalReg, sourceRegs=['$fp'], offset=victimOffset)
    ]

# puts saves a victim onto the stack so that its physical register can be safely overwritten
def _stashReg(victim, regMap, frameMap):
    physicalReg = regMap[victim]
    victimOffset = frameMap[victim]
    return [
        MIPSInstruction('sw', targetReg='$fp', sourceRegs=[physicalReg], offset=victimOffset),
    ]

def _getFrameMap(regMap):
    frameMap = {}
    i = 0
    for reg in regMap.keys():
        frameMap[reg] = i * -4
        i += 1
    return frameMap

def _insertFrameSetup(instructions, regMap, argCount=0):
    # Assume that the calling convention will set the value of $fp
    frameOffset = len(regMap.keys()) * -4
    instructions.insert(argCount, MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=frameOffset))

def _insertFrameBreakDown(instructions, frameMap):
    if len(instructions) > 0:
        frameOffset = len(frameMap.keys()) * 4
        if instructions[-1].op == 'jr':
            instructions.insert(-1, MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=frameOffset))
        else:
            instructions.append(MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=frameOffset))

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
    instructions = [
        MIPSInstruction('sw', targetReg='s1', sourceRegs=['s0'], offset=4)
    ]

    regMap = {
        'a'     : '$t0',
        'b'     : '$t1',
        's0'    : None,
        's1'    : None,
        'c'     : '$t2',
        't'     : None, 
    }

    frameMap = {
        'a'     :   0,
        'b'     :   4,
        's0'    :   8,
        's1'    :   12,
        'c'     :   16,
        't'     :   20
    }


    output = _mapInstruction(instructions[0], regMap, frameMap)
    for i in output:
        print(i)

if __name__ == "__main__":
    main()