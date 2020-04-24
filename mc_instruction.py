RWMEM = ['lb', 'lw', 'sb', 'sw']
branches = ['beq', 'blt', 'bgt', 'ble', 'bge', 'bne', 'blez']

class MCInstruction:
    def __init__(self, op, regs=None, imm=None, offset=None, target=None,
                 function_name=None, arguments=None, return_dest=None, is_call_move=False):
        self.op = self._formatOp(op)
        self.regs = self._formatRegs(regs)
        self.imm = imm
        self.offset = offset
        self.target = target
        self.is_call_move = is_call_move

    def __str__(self):
        # NOTE: call and callr should never remain in the final output, so their string representation is mostly for debugging
        if self.op == "call":
            assert(self.function_name is not None)
            assert(self.arguments is not None)
            return "call:\n\
                    function_name: {}, arguments:{}".format(self.function_name, self.arguments)
        if self.op == "callr":
            assert(self.function_name is not None)
            assert(self.arguments is not None)
            assert(self.return_dest is not None)
            return "callr:\n\
                    return_dest: {}, function_name: {}, arguments:{}".format(self.return_dest, self.function_name, self.arguments)
        if self.op == 'label':
            return self.target + ':'
        if self.op == 'noop':
            return self.op
        if self.op in RWMEM:
            if self.offset:
                return '\t{} {}, {}({})'.format(self.op, self.regs[0], self.offset, self.regs[1]) 
            else:
                return '\t{} {}, ({})'.format(self.op, self.regs[0], self.regs[1]) 
        outstr = "\t" + self.op
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
            return [r for r in reg]
        return reg
