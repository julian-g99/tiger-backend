from mc_instruction import MCInstruction
import heapq

TARGETS = {'$t':3}
ZREG = '$zero'
SPREG = '$sp'

# For special case handling in calculating live ranges
USEALLREGS = [
    'beq',
    'bgez',
    'bgezal',
    'bgtz',
    'blez',
    'bltz',
    'bltzal',
    'bne',
    'div',
    'divu',
    'jr',
    'mult',
    'multu',
    'sw',
    'sb',
    ]

class MIPSAllocator:
    def __init__(self, program):
        if type(program) != list:
            raise TypeError("program must be of type list. Got {}".format(type(program)))
        for instruction in program:
            if type(instruction) != MCInstruction:
                raise TypeError("All elements of program must be of type MCInstruction. Got {}".format(type(instruction)))
        self.program = program
    
    def _canAlloc(self, target):
        return TARGETS[target] >= 3  # Further optimization could allow for this number to be 2
    
    def _genStackAlloc(self):
        return (
            MCInstruction('addi', regs=[SPREG, SPREG], imm=-4),
            MCInstruction('sw', regs=[ZREG, SPREG], offset=0)
        )
    
    def _genStackStore(self, preg, offset=0):
        if type(preg) != str:
            raise TypeError("preg must be of type str. Got {}".format(type(preg)))
        if type(offset) != int:
            raise TypeError("offset must be of type int. Got {}".foramt(type(offset)))
        return MCInstruction('sw', regs=[preg, SPREG], offset=offset)
    
    def _genStackLoad(self, preg, offset=0):
        if type(preg) != str:
            raise TypeError("preg must be of type str. Got {}".format(type(preg)))
        if type(offset) != int:
            raise TypeError("offset must be of type int. Got {}".foramt(type(offset)))
        return MCInstruction('lw', regs=[preg, SPREG], offset=offset)
    
    def _getVirtualRegs(self, target):
        regs = []
        for instruction in self.program:
            if instruction.regs != None:
                for r in instruction.regs:
                    if (r[:2] == target) & (r not in regs):
                        regs.append(r)
        return regs

    def _getPhysicalRegs(self, target):
        pregCount = TARGETS[target]
        pregs = []
        for i in range(0, pregCount):
            pregs.append(target + str(i))
        return pregs
    
    # Returns the immutable value of an instruction if it modifies the stack pointer. Else return 0.
    # This is used to help track the offset of the stack pointer to the area on the stack where space is cleared
    # for all virtual registers
    def _getStackModifierImm(self, instruction):
        if type(instruction) != MCInstruction:
            raise Exception("instruction must be of type MCInstruction. Got {}".format(type(instruction)))
        if instruction.op == 'addi':
            if (instruction.regs is None) | (len(instruction.regs) == 0) | (instruction.imm is None):
                raise ValueError("Instruction is improperly formatted: {}".format(str(instruction)))
            if instruction.regs[0] == SPREG:
                return instruction.imm
        return 0
    


class NaiveMIPSAllocator(MIPSAllocator):
    def __init__(self, program):
        super().__init__(program)
    
    def allocTarget(self, target='$t'):
        if type(target) != str:
            raise TypeError("target {} must be of type str. Got {}".format(target, type(target)))
        if not (target in TARGETS):
            raise ValueError("target {} is invalid".format(target))
        if not self._canAlloc(target):
            raise ValueError("There are not enough target registers to allocate target {}".format(target))
        vregs = self._getVirtualRegs(target)
        pregs = self._getPhysicalRegs(target)
        newProgram = []
        newProgram.append(self.program[0]) # assume first instruction is main label
        # 1) insert stack allocs. This must be the first modification of the stack pointer
        for i in range(0, len(vregs)):
            vr = vregs[i]
            i1, i2 = self._genStackAlloc()
            newProgram.append(i1)
            newProgram.append(i2)
        regPointerOffset = 0
        # 2) insert load, original, and store instructions. We track the stack pointer offset since step 1.
        for i in range(1, len(self.program)):
            instruction = self.program[i]
            regPointerOffset -= self._getStackModifierImm(instruction) # calculate the new stack pointer offset since step 1
            # insert pre instruction loads
            if instruction.regs != None:
                for j in range(0, len(instruction.regs)):
                    vr = instruction.regs[j]
                    if vr in vregs:
                        pr = pregs[j]
                        offset = self._getStackOffset(vr, vregs, regPointerOffset)
                        newProgram.append(self._genStackLoad(pr, offset=offset))
                        # print(newProgram[-1])
            # insert original instruction with new registers mapped
            newInstruction = self._mapInstructionRegs(instruction, vregs, pregs)
            newProgram.append(newInstruction)
            # print(newProgram[-1])
            # insert post instruction stores
            if instruction.regs != None:
                for j in range(0, len(instruction.regs)):
                    vr = instruction.regs[j] # assumes the only register ever updated in an instruction is the first one
                    if vr in vregs:
                        pr = pregs[j]
                        offset = self._getStackOffset(vr, vregs, regPointerOffset)
                        newProgram.append(self._genStackStore(pr, offset=offset))
                        # print(newProgram[-1])
        return newProgram

    def _mapInstructionRegs(self, instruction, vregs=[], pregs=[]):
        if type(instruction) != MCInstruction:
            raise TypeError("instruction must be of type MCInstruction. Got {}".format(type(instruction)))
        if type(vregs) != list:
            raise TypeError("vregs must be of type list. Got {}".format(type(vregs)))
        if type(pregs) != list:
            raise TypeError("pregs must be of type list. Got {}".format(type(pregs)))
        if instruction.regs == None:
            return instruction
        op = instruction.op
        imm = instruction.imm
        offset = instruction.offset
        regs = []
        for i in range(0, len(instruction.regs)):
            r = instruction.regs[i]
            if r in vregs:
                regs.append(pregs[i])
            else:
                regs.append(r)
        return MCInstruction(op, regs=regs, imm=imm, offset=offset)
    
    # This calculates the exact offset from the stack pointer to the area on the stack a given
    # virtual is saved to.
    def _getStackOffset(self, vr, vregs, regPointerOffset):
        return vregs.index(vr) * 4 + regPointerOffset


class GreedyMIPSAllocator(MIPSAllocator):
    def __init__(self, program):
        super().__init__(program)
        self._resetAllocParams()
    
    def _resetAllocParams(self):
        self.sregPointerOffset = 0
        self.regMap = {}
        self.vregs = []
        self.pregs = []
        self.sregs = []
        self.newProgram = []

    def allocTarget(self, target='$t'):
        if type(target) != str:
            raise TypeError("target {} must be of type str. Got {}".format(target, type(target)))
        if not (target in TARGETS):
            raise ValueError("target {} is invalid".format(target))
        if not self._canAlloc(target):
            raise ValueError("There are not enough target registers to allocate target {}".format(target))
        self._resetAllocParams()
        self.vregs = self._getVirtualRegs(target)
        self.pregs = self._getPhysicalRegs(target)
        liveranges = self._getLiveRanges()
        self.regMap = self._getRegMap(liveranges)
        print(liveranges)
        print(self.regMap)
        self.sregs = self.regMap['spill']
        for sr in self.sregs:
            self._insertStackAlloc()
        self.sregPointerOffset = 0
        for instruction in self.program:
            self._checkForModifiedSP(instruction)
            sregMap = self._getSregMap(instruction)
            for sr in sregMap.keys():
                self._insertPregStore(sregMap[sr])
                self._insertSregLoad(sr, sregMap[sr])
            self._insertMappedInstruction(instruction, sregMap)
            for sr in sregMap.keys():
                self._insertSregStore(sr, sregMap[sr])
                self._insertPregLoad(sregMap[sr])
        return self.newProgram

    # inserts 2 instructions to allocate empty space on the stack for spilled registers
    def _insertStackAlloc(self):
        self.newProgram.append(MCInstruction('addi', regs=[SPREG, SPREG], imm=-4))
        self.newProgram.append(MCInstruction('sw', regs=[ZREG, SPREG], offset=0))
    
    # inserts instruction for loading the value of a spilled reg into a given phyiscal reg
    def _insertSregLoad(self, sr, preg):
        offset = self._getStackOffset(sr)
        self.newProgram.append(MCInstruction('lw', regs=[preg, SPREG], offset=offset))
    
    # inserts instruction for storing the value of a physical reg onto the area of the stack for a given spilled reg
    def _insertSregStore(self, sr, preg):
        if type(preg) != str:
            raise TypeError("preg must be of type str. Got {}".format(type(preg)))
        offset = self._getStackOffset(sr)
        self.newProgram.append(MCInstruction('sw', regs=[preg, SPREG], offset=offset))
    
    # pops a value off the stack and loads it into the given physical reg
    def _insertPregLoad(self, preg):
        self.newProgram.append(MCInstruction('lw', regs=[preg, SPREG], offset=0))
        self.newProgram.append(MCInstruction('addi', regs=[SPREG, SPREG], imm=4))
        self.sregPointerOffset -= 4

    # pushes the value of a given physical reg onto the stack
    def _insertPregStore(self, preg):
        self.newProgram.append(MCInstruction('addi', regs=[SPREG, SPREG], imm=-4))
        self.newProgram.append(MCInstruction('sw', regs=[preg, SPREG], offset=0))
        self.sregPointerOffset += 4

    # checks if an instruction (addi only) modifies the value of the stack pointer and tracks it accordingly
    def _checkForModifiedSP(self, instruction):
        if type(instruction) != MCInstruction:
            raise Exception("instruction must be of type MCInstruction. Got {}".format(type(instruction)))
        if (instruction.regs != None) and (instruction.regs[0] == SPREG):
            if instruction.op == 'addi':
                if (len(instruction.regs) == 0) | (instruction.imm is None):
                    raise ValueError("Instruction is improperly formatted: {}".format(str(instruction)))
                self.regStackOffset += instruction.imm
            else:
                raise ValueError('Instruction {} modifies stack pointer incorrectly'.format(instruction))
    
    # computes the offset of the stack location containing the value of a given spilled reg for load and store instructions
    def _getStackOffset(self, sr):
        return self.sregs.index(sr) * 4 + self.sregPointerOffset

    # inserts an instruction with its virtual registers replaced with phyical ones
    def _insertMappedInstruction(self, instruction, sregMap):
        if instruction.regs == None:
            self.newProgram.append(instruction)
            return
        op = instruction.op
        imm = instruction.imm
        offset = instruction.offset
        regs = []
        for r in instruction.regs:
            if r in self.regMap.keys():
                regs.append(self.regMap[r])
            elif r in sregMap.keys():
                regs.append(sregMap[r])
            else:
                regs.append(r)
        self.newProgram.append(MCInstruction(op, regs=regs, imm=imm, offset=offset))
    
    # computes a legal mapping of spilled virtual registers to physical ones for a given instruction
    def _getSregMap(self, instruction):
        sregMap = {}
        if instruction.regs == None:
            return sregMap
        mapped = self._getInstructionMappedPregs(instruction)
        for reg in instruction.regs:
            if reg in self.sregs:
                if len(mapped) == len(self.pregs):
                    raise ValueError('Register {} from instruction {} cannot be mapped. Ran out of available physical registers'.format(reg, instruction))
                for pr in self.pregs:
                    if pr not in mapped:
                        sregMap[reg] = pr
                        mapped.append(pr)
        return sregMap
    
    # computes a legal mapping of virtual regs to physical ones for the entire program, spilling some regs if necessary
    def _getRegMap(self, liveranges):
        regMap = {}
        regMap['spill'] = []
        mapped = []
        i = 0
        while i < len(self.pregs):
            maxVreg = None
            for vr in liveranges.keys():
                if (maxVreg == None) or (len(liveranges[vr]) > len(liveranges[maxVreg])):
                    if vr not in mapped:
                        maxVreg = vr
            if maxVreg == None:
                return regMap
            regMap[maxVreg] = self.pregs[i]
            i += 1
            mapped.append(maxVreg)
        if len(mapped) < len(liveranges.keys()):
            for vr in liveranges.keys():
                if vr not in mapped:
                    regMap['spill'].append(vr)
        return regMap
    
    # returns the to be mapped physical regs of an instruction
    def _getInstructionMappedPregs(self, instruction):
        pregs = []
        if instruction.regs == None:
            return pregs
        for reg in instruction.regs:
            if reg in self.regMap.keys():
                pregs.append(self.regMap[reg])
        return pregs

    # computes the live ranges of all virtual regs
    def _getLiveRanges(self):
        lastUse = {}
        ranges = {}
        for vr in self.vregs:
            lastUse[vr] = -1
            ranges[vr] = []
        for i in range(0, len(self.program)):
            instruction = self.program[i]
            _def = self._getDef(instruction)
            if _def in self.vregs:
                if (_def != None):
                    self._deleteAfterLastUse(_def, lastUse[_def], ranges)
                    lastUse[_def] = i
                uses = self._getUses(instruction)
            for use in uses:
                if use in self.vregs:
                    lastUse[use] = i
            for vr in self.vregs:
                ranges[vr].append(i)
        for vr in self.vregs:
            self._deleteAfterLastUse(vr, lastUse[vr], ranges)
        return ranges

    # returns the virtual regs used in this instruction (according to definition of a use)
    def _getUses(self, instruction):
        if (instruction.regs == None) or (len(instruction.regs) == 0):
            return []
        if instruction.op in USEALLREGS:
            return instruction.regs
        else:
            return instruction.regs[1:]
    
    # returns the virtual regs defined in this instruction
    def _getDef(self, instruction):
        if (instruction.regs == None) or (len(instruction.regs) == 0):
            return None
        if instruction.op in USEALLREGS:
            return None
        else:
            return instruction.regs[0]
    
    # helper method used in self._getLiveRanges()
    def _deleteAfterLastUse(self, _def, lastUse, ranges):
        if lastUse < 0:
            ranges[_def] = []
            return
        if lastUse-1 < 0:
            raise ValueError("def {} cannot be alive before program start".format(_def))
        delIdx = ranges[_def].index(lastUse)
        ranges[_def] = ranges[_def][:delIdx]

def main():
    # program = [
    #     MCInstruction("label", target="main"),
    #     MCInstruction("addi", regs=["$t0", "$zero"], imm=1),
    #     MCInstruction("addi", regs=["$t1", "$zero"], imm=2),
    #     MCInstruction("add", regs=["$t2", "$t0", "$t1"]),
    #     MCInstruction("add", regs=["$a0", "$t1", "$t2"]),
    #     MCInstruction("jal", target="func"),

    #     MCInstruction("add", regs=["$s0", "$t2", "$t1"]),
    #     MCInstruction("addi", regs=["$s0", "$s0"], imm=9),
    #     MCInstruction("label", target="end"),
    #     MCInstruction("j", target="end"),

    #     MCInstruction("label", target="func"),
    #     MCInstruction("addi", regs=["$sp", "$sp"], imm=-12),
    #     MCInstruction("sw", regs=["$t0", "$sp"], offset=0),
    #     MCInstruction("sw", regs=["$t1", "$sp"], offset=4),
    #     MCInstruction("sw", regs=["$t2", "$sp"], offset=8),
    #     MCInstruction("addi", regs=["$t0", "$zero"], imm=5),
    #     MCInstruction("addi", regs=["$t1", "$zero"], imm=7),
    #     MCInstruction("add", regs=["$t2", "$t1", "$t0"]),
    #     MCInstruction("addi", regs=["$v0", "$t2"], imm=3),
    #     MCInstruction("lw", regs=["$t0", "$sp"], offset=0),
    #     MCInstruction("lw", regs=["$t1", "$sp"], offset=4),
    #     MCInstruction("lw", regs=["$t3", "$sp"], offset=8),
    #     MCInstruction("addi", regs=["$sp", "$sp"], imm=12),
    #     MCInstruction("jr", regs=["$ra"]),
    # ]
    program = [
        MCInstruction('addi', regs=['$t3', '$zero'], imm=1),
        MCInstruction('addi', regs=['$t1', '$zero'], imm=2),
        MCInstruction('addi', regs=['$t0', '$zero'], imm=4),
        MCInstruction('add', regs=['$t2', '$t3', '$t1']),
        MCInstruction('sub', regs=['$t1', '$t2', '$t3']),
        MCInstruction('addi', regs=['$t2', '$t0'], imm=3),
        MCInstruction('add', regs=['$t3', '$t3', '$t3']),
        MCInstruction('add', regs=['$t2', '$t1', '$t3']),
        MCInstruction('add', regs=['$t0', '$t1', '$t2']),
        MCInstruction('add', regs=['$a0', '$zero', '$t0']),
        MCInstruction('label', target='end'),
        MCInstruction('j', target='end'),
    ]

    print("original code:\n")
    for instruction in program:
        print(instruction)
    
    print("\n\nallocated code:\n")

    # nalloc = NaiveMIPSAllocator(program)
    # newProgram = nalloc.allocTarget('$t')
    # for instruction in newProgram:
    #     print(instruction)
    galloc = GreedyMIPSAllocator(program)
    newProgram = galloc.allocTarget('$t')
    for i in newProgram:
        print(i)


if __name__ == "__main__":
    main()

