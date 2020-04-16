RWMEM = ['lb', 'lw', 'sb', 'sw']
branches = ['beq', 'blt', 'bgt', 'ble', 'bge', 'bne']

class MCInstruction:
    def __init__(self, op, regs=None, imm=None, offset=None, target=None,
                 function_name=None, arguments=None):
        self.op = self._formatOp(op)
        self.regs = self._formatRegs(regs)
        self.imm = imm
        self.offset = offset
        self.target = target

    def __str__(self):
        if self.op == "call" or self.op == "callr":
            assert(self.function_name is not None)
            assert(self.arguments is not None)
            return self.op + self.function_name + ", " + ", ".join(self.arguments)
        if self.op == 'label':
            return self.target + ':'
        if self.op == 'noop':
            return self.op
        if self.op in RWMEM:
            if self.offset:
                return '{} {}, {}({})'.format(self.op, self.regs[0], self.offset, self.regs[1]) 
            else:
                return '{} {}, ({})'.format(self.op, self.regs[0], self.regs[1]) 
        outstr = self.op
        if self.regs != None:
            outstr += ' ' + ', '.join(self.regs)
        if self.imm != None:
            outstr += ', ' + str(self.imm)
        if self.target != None:
            if self.op in branches:
                outstr += ', ' + self.target
            else:
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
