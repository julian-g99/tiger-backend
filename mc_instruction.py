rtype = ['add', 'addu', 'and', 'or', 'sllv', 'slt', 'sltu', 'srlv', 'sub', 'subu', 'xor', 'mfhi', 'mflo']
itype = ['addi', 'addiu', 'andi', 'ori', 'sll', 'slti', 'sltiu', 'sra', 'srl', 'xori', 'lb', 'lui', 'lw', 'sw', 'bne']
jtype = ['beg', 'bgeq', 'bgezal', 'bgtz', 'blez', 'bltz', 'bltzal', 'j', 'jal', 'jr', 'label', 'noop']
RWMEM = ['lb', 'lw', 'sb', 'sw']
WREG = [
    'add',
    'addu',
    'and',
    'or',
    'sllv',
    'slt',
    'sltu',
    'srlv',
    'sub',
    'subu',
    'xor',
    'mfhi',
    'mflo',
    'addi',
    'addiu',
    'andi',
    'ori',
    'sll',
    'slti',
    'sltiu',
    'sra',
    'srl',
    'xori',
    'lb',
    'lui',
    'lw'
]

TARGETS = {'$t':10}
ZREG = '$zero'
SPREG = '$sp'


class MCInstruction:
    def __init__(self, op, regs=None, imm=None, offset=None, target=None):
        self.op = self._formatOp(op)
        self.regs = self._formatRegs(regs)
        self.imm = imm
        self.offset = offset
        self.target = target
    
    def __str__(self):
        if self.op == 'label':
            return self.target + ':'
        if self.op == 'noop':
            return self.op
        if self.op in RWMEM:
            return '{} {} {}({})'.format(self.op, self.regs[0], self.offset, self.regs[1]) 
        outstr = self.op
        if self.regs != None:
            outstr += ' ' + ', '.join(self.regs)
        if self.imm != None:
            outstr += ' ' + str(self.imm)
        if self.target != None:
            outstr += ' ' + self.target
        return outstr
    
    def _formatOp(self, op):
        if op == None:
            return op
        return op.lower()
    
    def _formatRegs(self, reg):
        if reg == None:
            return None
        if type(reg) == list:
            return [r.lower() for r in reg]
        return reg.lower()


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
    
    def _genStackAlloc(self, offset=0):
        if type(offset) != int:
            raise TypeError("offset must be of type int. Got {}".format(type(offset)))
        return (
            MCInstruction('addi', regs=[SPREG, SPREG], imm=-4),
            MCInstruction('sw', regs=[ZREG, SPREG], offset=offset)
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

        # 1) insert stack allocs. This must be the first modification of the stack pointer
        newProgram.append(MCInstruction('label', target='main')) # assume first instruction is always the main label
        for i in range(1, len(vregs)):
            vr = vregs[i]
            offset = i*4
            i1, i2 = self._genStackAlloc(offset=offset)
            newProgram.append(i1)
            newProgram.append(i2)
        regPointerOffset = 0

        # 2) insert load, original, and store instructions. We track the stack pointer offset since step 1.
        for instruction in self.program:
            regPointerOffset += self._getStackModifierImm(instruction) # calculate the new stack pointer offset since step 1
            # insert pre instruction loads
            if instruction.op in WREG:
                if len(instruction.regs) > 1:
                    for j in range(1, len(instruction.regs)):
                        vr = instruction.regs[j]
                        if vr in vregs:
                            pr = pregs[j]
                            offset = self._getStackOffset(vr, vregs, regPointerOffset) * 4
                            newProgram.append(self._genStackLoad(pr, offset=offset))
            # insert original instruction with new registers mapped
            newInstruction = self._mapInstructionRegs(instruction, vregs, pregs)
            newProgram.append(newInstruction)
            # insert post instruction stores
            if instruction.op in WREG: 
                vr = instruction.regs[0] # assumes the only register ever updated in an instruction is the first one
                if vr in vregs:
                    pr = pregs[0]
                    offset = self._getStackOffset(vr, vregs, regPointerOffset) * 4
                    newProgram.append(self._genStackStore(pr, offset=offset))
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
        regs = []
        pregIdx = 0
        for r in instruction.regs:
            if r in vregs:
                regs.append(pregs[pregIdx])
                pregIdx += 1
            else:
                regs.append(r)
        return MCInstruction(op, regs=regs, imm=imm)
    
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
    
    # This calculates the exact offset from the stack pointer to the area on the stack a given
    # virtual is saved to.
    def _getStackOffset(self, vr, vregs, regPointerOffset):
        return vregs.index(vr) + regPointerOffset


def main():
    program = [
        MCInstruction("label", target="main"),
        MCInstruction("addi", regs=["$t0", "$zero"], imm=5),
        MCInstruction("addi", regs=["$t1", "$zero"], imm=10),
        MCInstruction("add", regs=["$t2", "$t0", "$t1"]),
        MCInstruction("add", regs=["$a0", "$t1", "$t2"]),
        MCInstruction("jal", target="func"),

        MCInstruction("label", target="end"),
        MCInstruction("j", target="end"),

        MCInstruction("label", target="func"),
        MCInstruction("addi", regs=["$sp", "$sp"], imm=-12),
        MCInstruction("sw", regs=["$t0", "$sp"], offset=0),
        MCInstruction("sw", regs=["$t1", "$sp"], offset=4),
        MCInstruction("sw", regs=["$t2", "$sp"], offset=8),
        MCInstruction("addi", regs=["$t0", "$zero"], imm=10),
        MCInstruction("addi", regs=["$v0", "$t0"], imm=11),
        MCInstruction("lw", regs=["$t0", "$sp"], offset=0),
        MCInstruction("lw", regs=["$t1", "$sp"], offset=4),
        MCInstruction("sw", regs=["$t3", "$sp"], offset=8),
        MCInstruction("addi", regs=["$sp", "$sp"], imm=12),
        MCInstruction("jr", regs=["$ra"]),
    ]

    print("original code:\n")
    for instruction in program:
        print(instruction)
    
    print("\n\nallocated code:\n")

    nalloc = NaiveMIPSAllocator(program)
    newProgram = nalloc.allocTarget('$t')
    for instruction in newProgram:
        print(instruction)


if __name__ == "__main__":
    main()

