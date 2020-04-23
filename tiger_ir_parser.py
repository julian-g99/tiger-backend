from mips_instruction import MIPSInstruction
import re

binary_ops = ['add', 'sub', 'mult', 'div', 'and', 'or']
assign_ops = ['assign']
goto_ops = ['goto']
branch_ops = ['breq', 'brneq', 'brlt', 'brgt', 'brgeq', 'brleq']
return_ops = ['return']
call_ops = ['call']
callr_ops = ['callr']
array_store_ops = ['array_store']
array_load_ops = ['array_load']
intrinsics = ['geti', 'getc', 'puti', 'putc']

regex_var = re.compile("[a-zA-Z_][a-zA-z0-9_]*")
regex_imm = re.compile("[0-9]+")
regex_label = re.compile("[a-zA-Z_][a-zA-z0-9_]*:")

opcodeParseTable = {
    'add'           :   'add',
    'sub'           :   'sub',
    'mult'          :   'mult',
    'div'           :   'div',
    'and'           :   'and',
    'or'            :   'or',
    'assign'        :   'move',
    'goto'          :   'j',
    'breq'          :   'beq',
    'brneq'         :   'bne',
    'brlt'          :   'bltz',
    'brgt'          :   'bgtz',
    'brgeq'         :   'bgez',
    'brleq'         :   'blez',
    'return'        :   'jr',
    'call'          :   'jal',
    'callr'         :   'jal',
    'array_store'   :   None,
    'array_load'    :   None,
}

immOpcodeParseTable = {
    'add'           :   'addi',
    'sub'           :   None,
    'mult'          :   None,
    'div'           :   None,
    'and'           :   'andi',
    'or'            :   'ori',
    'assign'        :   None,
    'goto'          :   None,
    'breq'          :   None,
    'brneq'         :   None,
    'brlt'          :   None,
    'brgt'          :   None,
    'brgeq'         :   None,
    'brleq'         :   None,
    'return'        :   None,
    'call'          :   None,
    'callr'         :   None,
    'array_store'   :   None,
    'array_load'    :   None,
}

# The return function cannot be parsed before calling convention is inserted so it is put in a shell MIPSInstruction.
# This method is used during the calling convention step to finish the parsing of the return instruction
def parseJR(instruction):
    sourceRegs = instruction.sourceRegs
    imm = instruction.imm
    if imm != None:
        return [
            MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imm),
            MIPSInstruction('sw', targetReg='$sp', sourceRegs=['!x0'], offset=0),
            MIPSInstruction('jr', sourceRegs=['$ra'])
        ]
    else:
        return [
            MIPSInstruction('sw', targetReg='$sp', sourceRegs=sourceRegs, offset=0),
            MIPSInstruction('jr', sourceRegs=['$ra'])
        ]

def parseLine(line):
    if _isLabel(line):
        return [ MIPSInstruction('label', target=line[:-1]) ]
    tokens = line.split(",")
    tokens = [t.strip(" ") for t in tokens]
    if len(tokens) < 1:
        raise ValueError("Failed to divide line {} into tokens".format(line))
    
    op = tokens[0]
    if op in binary_ops:
        return _parseBinary(tokens)
    elif op in assign_ops:
        return _parseAssign(tokens)
    elif op in goto_ops:
        return _parseGoto(tokens)
    elif op in branch_ops:
        return _parseBranch(tokens)
    elif op in return_ops:
        return _parseReturn(tokens)
    elif op in call_ops:
        return _parseCall(tokens)
    elif op in callr_ops:
        return _parseCallr(tokens)
    elif op in array_store_ops:
        return _parseArrayStore(tokens)
    elif op in array_load_ops:
        return _parseArrayLoad(tokens)
    else:
        return [] # rejects lines that can't be parsed including blank lines

def _isVar(token):
    return re.fullmatch(regex_var, token) != None

def _isImm(token):
    return re.fullmatch(regex_imm, token) != None

def _isLabel(token):
    return re.fullmatch(regex_label, token) != None

def _parseBinary(tokens):
    regs = []
    imms = []
    for t in tokens[1:]:
        if _isVar(t):
            regs.append(t)
        elif _isImm(t):
            imms.append(t)
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    if len(imms) == 2:
        op = immOpcodeParseTable[tokens[0]]
        if op != None:
            return [
                MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imms[0]),
                MIPSInstruction(op, targetReg=regs[0], sourceRegs=['!x0'], imm=imms[1])
            ]
        else:
            op = opcodeParseTable[tokens[0]]
            return [
                MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imms[0]),
                MIPSInstruction('addi', targetReg='!x1', sourceRegs=['$zero'], imm=imms[1]),
                MIPSInstruction(op, targetReg=regs[0], sourceRegs=['!x0, !x1'])
            ]
    elif len(imms) == 1:
        op = immOpcodeParseTable[tokens[0]]
        if op != None:
            return [
                MIPSInstruction(op, targetReg=regs[0], sourceRegs=[regs[1]], imm=imms[0]),
            ]
        else:
            op = opcodeParseTable[tokens[0]]
            return [
                MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imms[0]),
                MIPSInstruction(op, targetReg=regs[0], sourceRegs=[regs[1], '!x0'])
            ]
    elif len(regs) == 3:
        op = opcodeParseTable[tokens[0]]
        return [
            MIPSInstruction(op, targetReg=regs[0], sourceRegs=regs[1:])
        ]
    else:
        raise ParseException("Failed to parse token list: {}".format(tokens))

def _parseAssign(tokens):
    if len(tokens) == 4:
        return _parseArrayAssign(tokens)
    regs = []
    imm = None
    for t in tokens[1:]:
        if _isVar(t):
            regs.append(t)
        elif _isImm(t):
            imm = t
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    if len(regs) < 0:
        raise ParseException("Could not find a variable in tokens: {}".format(tokens))
    op = opcodeParseTable[tokens[0]]
    if imm != None:
        return [
            MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imm),
            MIPSInstruction(op, targetReg=regs[0], sourceRegs=['!x0'])
        ]
    else:
        return [
            MIPSInstruction(op, targetReg=regs[0], sourceRegs=[regs[1]])
        ]
    
def _parseArrayAssign(tokens):
    name = tokens[1]
    size = int(tokens[2]) * 4
    return [
        MIPSInstruction('li', targetReg='$v0', imm=9),
        MIPSInstruction('la', targetReg='$a0', imm=size),
        MIPSInstruction('syscall'),
        MIPSInstruction('move', targetReg=name, sourceRegs=['$v0'])
    ]

def _parseGoto(tokens):
    op = opcodeParseTable[tokens[0]]
    target = tokens[1]
    return [MIPSInstruction(op, target=target)]

def _parseBranch(tokens):
    regs = []
    imm = None
    target = tokens[1]
    for t in tokens[2:]: # excludde the target by starting at 2
        if _isVar(t):
            regs.append(t)
        elif _isImm(t):
            imm = t
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    if len(regs) < 0:
        raise ParseException("Could not find a variable in tokens: {}".format(tokens))
    if tokens[0] in ['breq', 'brneq']:
        op = opcodeParseTable[tokens[0]]
        if imm != None:
            return [
                MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imm),
                MIPSInstruction(op, sourceRegs=[regs[0], '!x0'], target=target)
            ]
        else:
            return [MIPSInstruction(op, sourceRegs=regs, target=target)]
    else:
        op = opcodeParseTable[tokens[0]]
        if (imm != None):
            return [
                MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imm),
                MIPSInstruction('sub', targetReg ='!x0', sourceRegs=[regs[0], '!x0']),
                MIPSInstruction(op, sourceRegs=['!x0'], target=target)
            ]
        else:
            return [
                MIPSInstruction('sub', targetReg='!x0', sourceRegs=regs),
                MIPSInstruction(op, sourceRegs=['!x0'], target=target)
            ]

def _parseReturn(tokens):
    regs = None
    imm = None
    if _isVar(tokens[1]):
        regs = [tokens[1]]
    elif _isImm(tokens[1]):
        imm = tokens[1]
    else:
        raise ParseException("Failed to parse token: {} of tokens: {}".format(tokens[1], tokens))
    op = opcodeParseTable[tokens[0]]
    if imm != None:
        return [
            MIPSInstruction(op, imm=imm) # To be parsed into more intructions later after calling convention
        ]
    else:
        return [
            MIPSInstruction(op, sourceRegs=[regs[0]]) # To be parsed into more intructions later after calling convention
        ]

def _parseArrayStore(tokens):
    regs = None
    imm = None
    arrayReg = tokens[2]
    offset = int(tokens[3]) * 4
    if _isVar(tokens[1]):
        regs = [tokens[1]]
    elif _isImm(tokens[1]):
        imm = tokens[1]
    else:
        raise ParseException("Failed to parse token: {} of tokens: {}".format(tokens[1], tokens))
    if imm != None:
        return [
            MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imm),
            MIPSInstruction('sw', targetReg=arrayReg, sourceRegs=['!x0'], offset=offset)
        ]
    else:
        return [
            MIPSInstruction('sw', targetReg=arrayReg, sourceRegs=regs, offset=offset)
        ]

def _parseArrayLoad(tokens):
    targetReg = tokens[1]
    arrayReg = tokens[2]
    offset = int(tokens[3]) * 4
    return [
        MIPSInstruction('lw', targetReg=targetReg, sourceRegs=[arrayReg], offset=offset)
        ]

# includes some calling convention
def _parseCall(tokens):
    instructions = []
    funcName = tokens[1]
    if funcName in intrinsics:
        return _parseIntrinsic(funcName, tokens[-1])
    # save args
    for t in tokens[2:]: # start at first arg
        instructions += _getStackAlloc(1)
        if _isVar(t):
            instructions += _getRegStore(t)
        elif _isImm(t):
            instructions += _getImmStore(t)
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    # jump and link
    op = opcodeParseTable[tokens[0]]
    instructions.append(MIPSInstruction(op, target=funcName))
    # pop args
    instructions += _getStackPop(len(tokens) - 2)
    return instructions

# includes some calling convention
def _parseCallr(tokens):
    op = opcodeParseTable[tokens[0]]
    returnReg = tokens[1]
    funcName = tokens[2]
    if funcName in intrinsics:
        return _parseIntrinsic(funcName, returnReg)
    instructions = []
    # save args
    for t in tokens[3:]: # start at first arg
        instructions += _getStackAlloc(1)
        if _isVar(t):
            instructions += _getRegStore(t)
        elif _isImm(t):
            instructions += _getImmStore(t)
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    # alloc for return value
    instructions += _getStackAlloc(1)
    # jump and link
    instructions.append(MIPSInstruction(op, target=funcName))
    # get return value
    instructions += _getRegLoad(returnReg)
    # pop return value and args
    instructions += _getStackPop(len(tokens) - 3 + 1)
    return instructions

def _parseIntrinsic(funcName, token):
    reg = None
    imm = None
    if _isVar(token):
        reg = token
    elif _isImm(token):
        imm = token

    if funcName == 'geti':
        return [
            MIPSInstruction('li', targetReg='$v0', imm=5),
            MIPSInstruction('syscall'),
            MIPSInstruction('move', targetReg=reg, sourceRegs=['$v0'])
        ]
    elif funcName == 'getc':
        return [
            MIPSInstruction('li', targetReg='$v0', imm=12),
            MIPSInstruction('syscall'),
            MIPSInstruction('move', targetReg=reg, sourceRegs=['$v0'])
        ]
    elif funcName == 'puti':
        if imm != None:
            return [
                MIPSInstruction('li', targetReg='$v0', imm=1),
                MIPSInstruction('la', targetReg='$a0', imm=imm),
                MIPSInstruction('syscall')
            ]
        else:
            return [
                MIPSInstruction('li', targetReg='$v0', imm=1),
                MIPSInstruction('move', targetReg='$a0', sourceRegs=[reg]),
                MIPSInstruction('syscall')
            ]
    elif funcName == 'putc':
        if imm != None:
            return [
                MIPSInstruction('li', targetReg='$v0', imm=11),
                MIPSInstruction('la', targetReg='$a0', imm=imm),
                MIPSInstruction('syscall')
            ]
        else:
            return [
                MIPSInstruction('li', targetReg='$v0', imm=11),
                MIPSInstruction('move', targetReg='$a0', sourceRegs=[reg]),
                MIPSInstruction('syscall')
            ]
    else:
        raise ParseException('encountered unrecognized intrinsic: {}'.format(funcName))

def _getStackAlloc(amount):
        imm = amount * -4
        return [ MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=imm) ]

def _getImmStore(imm):
    return [
        MIPSInstruction('addi', targetReg='!x0', sourceRegs=['$zero'], imm=imm),
        MIPSInstruction('sw', targetReg='$sp', sourceRegs=['!x0'], offset=0)
    ]

def _getRegStore(reg):
        return [ MIPSInstruction('sw', targetReg='$sp', sourceRegs=[reg], offset=0) ]

def _getRegLoad(reg):
        return [ MIPSInstruction('lw', targetReg=reg, sourceRegs=['$sp'], offset=0) ]

def _getStackPop(amount):
    imm = amount * 4
    return [ MIPSInstruction('addi', targetReg='$sp', sourceRegs=['$sp'], imm=imm) ]

class ParseException(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)

