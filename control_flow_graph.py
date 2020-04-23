from mips_instruction import MIPSInstruction

TERMINATORS = ['label', 'beq', 'bgez', 'bgtz', 'blez', 'bltz', 'bne', 'j']

class BB:
    def __init__(self, pp, instructions=None):
        if instructions == None:
            self.instructions = []
        else:
            self.instructions = instructions
        self.pp = pp

    def __iter__(self):
        return BBIterator(self)

    def __len__(self):
        return len(self.instructions)

    def __getitem__(self, item):
        return self.instructions[item]

    def getLeader(self):
        if len(self.instructions) > 0:
            return self.instruction[0]
        raise LookupError("Basic Block is empty and thus has no leader")

    def addInstruction(self, instruction):
        if type(instruction) != MIPSInstruction:
            raise TypeError("instruction must be of type MIPSInstruction. Got {}.".format(type(instruction)))
        self.instructions.append(instruction)

class BBIterator:
    def __init__(self, bb):
        self.bb = bb
        self._index = 0

    def __next__(self):
        if self._index < len(self.bb):
            result = self.bb[self._index]
            self._index += 1
            return result
        raise StopIteration

class CFG:
    def __init__(self, program):
        self.program = program
        self.adjList = {}
        self.bbs = []
        self._build()
    
    def getInstructionsFromBBs(self):
        instructions = []
        pps = []
        for bb in self.bbs:
            pps.append(bb.pp)
        pps.sort()
        for pp in pps:
            for bb in self.bbs:
                if pp == bb.pp:
                    for instruction in bb:
                        instructions.append(bb)
        return instructions

    def _build(self):
        if len(self.program) == 0:
            return None
        bb = BB(0, instructions=[self.program[0]])
        self.adjList[bb.pp] = []
        self._buildR(1, bb)

    def _buildR(self, pp, bb):
        if pp < len(self.program):
            instruction = self.program[pp]
            if type(instruction) != MIPSInstruction:
                raise TypeError("instruction must be of type MIPSInstruction. Got {}".format(type(instruction)))
            if instruction.op == 'jr':
                # terminate at jr instruction. There is no way to find the target of a jr instruction without simulating a MIPS cpu
                bb.addInstruction(instruction)
                self.bbs.append(bb)
                return
            if instruction.op not in TERMINATORS:
                bb.addInstruction(instruction)
                self._buildR(pp+1, bb)
            else:
                if instruction.op == 'label':
                    labelPP = pp
                    self.adjList[bb.pp].append(labelPP)
                    if labelPP not in self.adjList.keys():
                        labelBB = BB(labelPP, instructions=[instruction])
                        self.adjList[labelBB.pp] = []
                        self._buildR(labelPP+1, labelBB)
                else:
                    bb.addInstruction(instruction)
                    targetPP = self._getJumpTargetPP(instruction)
                    self.adjList[bb.pp].append(targetPP)
                    if targetPP not in self.adjList.keys():
                        labelInstruction = self.program[targetPP]
                        targetBB = BB(targetPP, instructions=[labelInstruction])
                        self.adjList[targetBB.pp] = []
                        self._buildR(targetPP+1, targetBB)
                    if instruction.op != 'j':
                        # only needed if jump is not unconditional
                        nextPP = pp + 1
                        if nextPP <= len(self.program):
                            self.adjList[bb.pp].append(nextPP)
                            if nextPP not in self.adjList.keys():
                                nextBB = BB(nextPP, instructions=[])
                                self.adjList[nextBB.pp] = []
                                if self.program[nextPP].op == 'label':
                                    nextBB.addInstruction(self.program[nextPP])
                                    nextPP += 1
                                self._buildR(nextPP, nextBB)
                self.bbs.append(bb)
        else:
            self.bbs.append(bb)

    def _getJumpTargetPP(self, jInstruction):
        if jInstruction.op == 'jr': # TODO: continue to think about this
            raise ValueError("CFG class can only build inner function control graphs. The jr instruction is treated as the end of the CFG, not a jtype instruction.")
        if jInstruction.target == None:
            raise ValueError("jtype Instruction must have a target")
        target = jInstruction.target
        for pp in range(0, len(self.program)):
            instruction = self.program[pp]
            if (instruction.op == 'label') and (instruction.target == target):
                return pp
        raise LookupError("did not find a label matching target {} for instruction {}"
                .format(target, jInstruction))
