from mc_instruction import MCInstruction
from control_flow_graph import CFG, BB
import heapq

PHYSICALS = {'$t':10, '$s':8}
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
        self.vregs = []
        self.pregs = []
    
    def _canAlloc(self, target):
        # return TARGETS[target] >= 3  # Further optimization could allow for this number to be 2
        return True

    def _genStackAlloc(self):
        return (
            MCInstruction('addi', regs=[SPREG, SPREG], imm=-4),
            MCInstruction('sw', regs=[ZREG, SPREG], offset=0)
        )
    
    def _getVirtualRegs(self, target):
        regs = []
        for instruction in self.program:
            if instruction.regs != None:
                for r in instruction.regs:
                    if (r[:len(target)] == target) & (r not in regs):
                        regs.append(r)
        return regs
    
    def _reformatRegMapSpillField(self, regMap):
        newRegMap = {}
        for reg in regMap.keys():
            if reg == 'spill':
                for sr in regMap['spill']:
                    newRegMap[sr] = 'spill'
            else:
                newRegMap[reg] = regMap[reg]
        return newRegMap

    def _getPhysicalRegs(self, target):
        pregCount = PHYSICALS[target]
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
    
class GreedyMIPSAllocator(MIPSAllocator):
    def __init__(self, program):
        super().__init__(program)
        self._resetAllocParams()
    
    # Clears all allocation params. Very important to call this method before every allocation attempt!
    def _resetAllocParams(self):
        self.sregPointerOffset = 0
        self.regMap = {}
        self.vregs = []
        self.pregs = []
        self.sregs = []
        self.newBlock = BB(0)

    def getRegMaps(self, target='$t', physical='$t'):
        cfg = CFG(self.program)
        regMaps = []
        for bb in cfg.bbs:
            regMap = self._getBlockRegMap(bb, target=target, physical=physical)
            regMap = self._reformatRegMapSpillField(regMap)
            regMaps.append({bb.pp: regMap})
        return regMaps
    
    def _getBlockRegMap(self, block, target='$t', physical='$t'):
        if type(target) != str:
            raise TypeError("target {} must be of type str. Got {}".format(target, type(target)))
        if not self._canAlloc(target):
            raise ValueError("There are not enough target registers to allocate target {}".format(target))
        self._resetAllocParams()
        self.newBlock.pp = block.pp
        self.vregs = self._getVirtualRegs(target)
        self.pregs = self._getPhysicalRegs(physical)
        liveranges = self._getLiveRanges(block)
        self.regMap = self._getRegMap(liveranges)
        return self.regMap

    def allocProgram(self, target='$t', physical='$t'):
        cfg = CFG(self.program)
        newBBs = []
        for bb in cfg.bbs:
            newBB = self._allocBlock(bb, target=target, physical='$t')
            newBBs.append(newBB)
        return newBBs

    def _allocBlock(self, block, target='$t', physical='$t'):
        if type(target) != str:
            raise TypeError("target {} must be of type str. Got {}".format(target, type(target)))
        if not self._canAlloc(target):
            raise ValueError("There are not enough target registers to allocate target {}".format(target))
        self._resetAllocParams()
        self.newBlock.pp = block.pp
        self.vregs = self._getVirtualRegs(target)
        self.pregs = self._getPhysicalRegs(physical)
        liveranges = self._getLiveRanges(block)
        self.regMap = self._getRegMap(liveranges)
        self.sregs = self.regMap['spill']
        for sr in self.sregs:
            self._insertStackAlloc()
        self.sregPointerOffset = 0
        for instruction in block:
            self._checkForModifiedSP(instruction)
            sregMap = self._getSregMap(instruction)
            for sr in sregMap.keys():
                self._insertPregStore(sregMap[sr])
                self._insertSregLoad(sr, sregMap[sr])
            self._insertMappedInstruction(instruction, sregMap)
            for sr in sregMap.keys():
                self._insertSregStore(sr, sregMap[sr])
                self._insertPregLoad(sregMap[sr])
        return self.newBlock

    # inserts 2 instructions to allocate empty space on the stack for spilled registers
    def _insertStackAlloc(self):
        self.newBlock.addInstruction(MCInstruction('addi', regs=[SPREG, SPREG], imm=-4))
        self.newBlock.addInstruction(MCInstruction('sw', regs=[ZREG, SPREG], offset=0))
    
    # inserts instruction for loading the value of a spilled reg into a given phyiscal reg
    def _insertSregLoad(self, sr, preg):
        offset = self._getStackOffset(sr)
        self.newBlock.addInstruction(MCInstruction('lw', regs=[preg, SPREG], offset=offset))
    
    # inserts instruction for storing the value of a physical reg onto the area of the stack for a given spilled reg
    def _insertSregStore(self, sr, preg):
        if type(preg) != str:
            raise TypeError("preg must be of type str. Got {}".format(type(preg)))
        offset = self._getStackOffset(sr)
        self.newBlock.addInstruction(MCInstruction('sw', regs=[preg, SPREG], offset=offset))
    
    # pops a value off the stack and loads it into the given physical reg
    def _insertPregLoad(self, preg):
        self.newBlock.addInstruction(MCInstruction('lw', regs=[preg, SPREG], offset=0))
        self.newBlock.addInstruction(MCInstruction('addi', regs=[SPREG, SPREG], imm=4))
        self.sregPointerOffset -= 4

    # pushes the value of a given physical reg onto the stack
    def _insertPregStore(self, preg):
        self.newBlock.addInstruction(MCInstruction('addi', regs=[SPREG, SPREG], imm=-4))
        self.newBlock.addInstruction(MCInstruction('sw', regs=[preg, SPREG], offset=0))
        self.sregPointerOffset += 4

    # computes the offset of the stack location containing the value of a given spilled reg for load and store instructions
    def _getStackOffset(self, sr):
        return self.sregs.index(sr) * 4 + self.sregPointerOffset

    # inserts an instruction with its virtual registers replaced with phyical ones
    def _insertMappedInstruction(self, instruction, sregMap):
        if instruction.regs == None:
            self.newBlock.addInstruction(instruction)
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
        self.newBlock.addInstruction(MCInstruction(op, regs=regs, imm=imm, offset=offset))
    
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
    def _getLiveRanges(self, block):
        lastUse = {}
        ranges = {}
        for vr in self.vregs:
            lastUse[vr] = -1
            ranges[vr] = []
        for i in range(0, len(block)):
            instruction = block[i]
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
        if lastUse < 0:
            raise ValueError("def {} cannot be alive at last use {}".format(_def, lastUse))
        delIdx = ranges[_def].index(lastUse)
        ranges[_def] = ranges[_def][:delIdx]

class NaiveMIPSAllocator(MIPSAllocator):
    def __init__(self, program):
        super().__init__(program)
        self._resetAllocParams()
    
    # Clears all allocation params. Very important to call this method before every allocation attempt!
    def _resetAllocParams(self):
        self.regPointerOffset = 0
        self.newProgram = []

    def getRegMap(self, target='$t', physical='$t'):
        if type(target) != str:
            raise TypeError("target {} must be of type str. Got {}".format(target, type(target)))
        if not self._canAlloc(target):
            raise ValueError("There are not enough target registers to allocate target {}".format(target))
        self._resetAllocParams()
        self.vregs = self._getVirtualRegs(target)
        regMap = {}
        regMap['spill'] = self.vregs
        regMap = self._reformatRegMapSpillField(regMap)
        return regMap

    def allocProgram(self, target='$t', physical='$t'):
        if type(target) != str:
            raise TypeError("target {} must be of type str. Got {}".format(target, type(target)))
        if not self._canAlloc(target):
            raise ValueError("There are not enough target registers to allocate target {}".format(target))
        self._resetAllocParams()
        self.vregs = self._getVirtualRegs(target)
        self.pregs = self._getPhysicalRegs(physical)
        for vr in self.vregs:
            self._insertStackAlloc()
        self.sregPointerOffset = 0
        for instruction in self.program:
            self._checkForModifiedSP(instruction)
            regMap = self._getRegMap(instruction)
            for vr in regMap.keys():
                self._insertVregLoad(vr, regMap[vr])
            self._insertMappedInstruction(instruction, regMap)
            for vr in regMap.keys():
                self._insertVregStore(vr, regMap[vr])
        return [BB(0, instructions=self.newProgram)]

    # inserts 2 instructions to allocate empty space on the stack for virtual registers
    def _insertStackAlloc(self):
        self.newProgram.append(MCInstruction('addi', regs=[SPREG, SPREG], imm=-4))
        self.newProgram.append(MCInstruction('sw', regs=[ZREG, SPREG], offset=0))
    
    # inserts instruction for loading the value of a virtual reg into a given phyiscal reg
    def _insertVregLoad(self, vr, pr):
        offset = self._getStackOffset(vr)
        self.newProgram.append(MCInstruction('lw', regs=[pr, SPREG], offset=offset))
    
    # inserts instruction for storing the value of a physical reg onto the area of the stack for a given virtual reg
    def _insertVregStore(self, vr, pr):
        if type(pr) != str:
            raise TypeError("preg must be of type str. Got {}".format(type(pr)))
        offset = self._getStackOffset(vr)
        self.newProgram.append(MCInstruction('sw', regs=[pr, SPREG], offset=offset))
    
    # computes the offset of the stack location containing the value of a given spilled reg for load and store instructions
    def _getStackOffset(self, vr):
        return self.vregs.index(vr) * 4 + self.regPointerOffset

    # inserts an instruction with its virtual registers replaced with phyical ones
    def _insertMappedInstruction(self, instruction, regMap):
        if instruction.regs == None:
            self.newProgram.append(instruction)
            return
        op = instruction.op
        imm = instruction.imm
        offset = instruction.offset
        regs = []
        for r in instruction.regs:
            if r in regMap.keys():
                regs.append(regMap[r])
            else:
                regs.append(r)
        self.newProgram.append(MCInstruction(op, regs=regs, imm=imm, offset=offset))
    
    # computes a legal mapping of virtual registers to physical ones for a given instruction
    def _getRegMap(self, instruction):
        regMap = {}
        if instruction.regs == None:
            return regMap
        for i in range(0, len(instruction.regs)):
            vr = instruction.regs[i]
            if vr in self.vregs:
                pr = self.pregs[i]
                regMap[vr] = pr
        return regMap


def main():
    pass
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
    # program = [
    #     MCInstruction('addi', regs=['$t3', '$zero'], imm=1),
    #     MCInstruction('addi', regs=['$t1', '$zero'], imm=2),
    #     MCInstruction('addi', regs=['$t0', '$zero'], imm=4),
    #     MCInstruction('add', regs=['$t2', '$t3', '$t1']),
    #     MCInstruction('sub', regs=['$t1', '$t2', '$t3']),
    #     MCInstruction('addi', regs=['$t2', '$t0'], imm=3),
    #     MCInstruction('add', regs=['$t3', '$t3', '$t3']),
    #     MCInstruction('add', regs=['$t2', '$t1', '$t3']),
    #     MCInstruction('add', regs=['$t0', '$t1', '$t2']),
    #     MCInstruction('add', regs=['$a0', '$zero', '$t0']),
    #     MCInstruction('label', target='end'),
    #     MCInstruction('j', target='end'),
    # ]
    # program = [
    #     MCInstruction('label', target='main'),
    #     MCInstruction('addi', regs=['$t0', '$zero'], imm=10),
    #     MCInstruction('label', target='loop'),
    #     MCInstruction('beq', regs=['$t0', '$zero'], target='exit'),
    #     MCInstruction('addi', regs=['$t2', '$t0'], imm=-5),
    #     MCInstruction('addi', regs=['$t3', '$t2'], imm=-5),
    #     MCInstruction('blez', regs=['$t1'], target='skip'),
    #     MCInstruction('addi', regs=['$t0', '$t0'], imm=-1),
    #     MCInstruction('j', target='loop'),
    #     MCInstruction('label', target='skip'),
    #     MCInstruction('addi', regs=['$t0', '$t0'], imm=-5),
    #     MCInstruction('j', target='loop'),
    #     MCInstruction('label', target='exit'),
    #     MCInstruction('j', target='exit')
    # ]

    # print("original code:\n")
    # for instruction in program:
    #     print(instruction)
    
    # print("\n\nallocated code:\n")

    # nalloc = NaiveMIPSAllocator(program)
    # newProgram = nalloc.allocProgram(target='$t')
    # for instruction in newProgram:
    #     print(instruction)
    # galloc = GreedyMIPSAllocator(program)
    # newBBs = galloc.allocProgram()
    # print(newBBs)
    # pp = []
    # for bb in newBBs:
    #     pp.append(bb.pp)
    # pp.sort()
    # for p in pp:
    #     for bb in newBBs:
    #         if bb.pp == p:
    #             for instruction in bb:
    #                 print(instruction)


if __name__ == "__main__":
    main()

