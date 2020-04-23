RWMEM = ['lb', 'lw', 'sb', 'sw']
branches = ['beq', 'blt', 'bgt', 'ble', 'bge', 'bne']

class MIPSInstruction:
    def __init__(self, op, targetReg=None, sourceRegs=None, imm=None, offset=None, target=None):
        self.op = self._formatOp(op)
        self.targetReg = self._formatRegs(targetReg)
        self.sourceRegs = self._formatRegs(sourceRegs)
        self.imm = imm
        self.offset = offset
        self.target = target

    def __str__(self):
        if self.op == 'label':
            return self.target + ':'
        if self.op == 'noop':
            return self.op
        if self.op == 'syscall':
            return self.op
        if self.op in 'sw':
            return '{} {}, {}({})'.format(self.op, self.sourceRegs[0], self.offset, self.targetReg)
        if self.op in 'lw':
            return '{} {}, {}({})'.format(self.op, self.targetReg, self.offset, self.sourceRegs[0])
        if self.op in ['jal', 'j']:
            return '{} {}'.format(self.op, self.target) 
        outstr = self.op
        regs = []
        if self.targetReg != None:
            regs.append(self.targetReg)
        if self.sourceRegs != None:
            regs += self.sourceRegs
    
        outstr += ' ' + ', '.join(regs)
        if self.imm != None:
            outstr += ', ' + str(self.imm)
        if self.target != None:
            if self.op in branches:
                outstr += ', ' + self.target
            else:
                outstr += ', ' + self.target
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
