from mc_instruction import MCInstruction

TERMINATORS = ['label', 'beq', 'bgez', 'bgtz', 'blez', 'bltz', 'bne', 'j']
LINKERS = ['bgezal', 'bltzal', 'jal']

class BB:
    def __init__(self, pp, instructions=[]):
        self.instructions = instructions
        self.pp = pp
    
    def add(self, instruction):
        self.instructions.append(0)

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
        self.bbs = []
        self._build()
    
    def _build(self):
        if len(self.program) == 0:
            return None
        bb = BB(0, instructions=[self.program[0]])
        self._buildR(1, bb)
    
    def _buildR(self, pp, bb):
        print(bb)
        if pp < len(self.program):
            nextBB = BB(pp)
            if (len(nextBB.instructions) > 0):
                print("bug still there:")
                for i in nextBB.instructions:
                    print('\t{}'.format(i))
            nextBB.add(self.program[pp])
            self._buildR(pp+1, nextBB)

def main():
    program = [
        MCInstruction('label', target='main'),
        MCInstruction('addi', regs=['$t0', '$zero'], imm=10),
        MCInstruction('label', target='loop'),
        MCInstruction('beq', target='exit'),
        MCInstruction('subi', regs=['$t1', '$t0'], imm=5),
        MCInstruction('blez', regs=['$t1'], target='skip'),
        MCInstruction('subi', regs=['$t0', '$t0'], imm=1),
        MCInstruction('j', target='loop'),
        MCInstruction('label', target='skip'),
        MCInstruction('subi', regs=['$t0', '$t0'], imm=5),
        MCInstruction('j', target='loop'),
        MCInstruction('label', target='exit'),
        MCInstruction('jr')
    ]

    cfg = CFG(program)

if __name__ == "__main__":
    main()