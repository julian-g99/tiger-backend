from mc_instruction import MCInstruction
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
    'sub'           :   'subi',
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


def parseLine(line):
    if _isLabel(line):
        return [ MCInstruction('label', target=line[:-1]) ]
    tokens = line.split(",")
    tokens = [t.strip(" ") for t in tokens]
    if len(tokens) < 1:
        raise ValueError("Failed to divide line {} into tokens".format(line))
    
    op = tokens[0]
    if op in binary_ops:
        return _parseBinary(tokens)
    elif op in assign_ops:
        return _parseAssign(tokens)
    elif op in branch_ops:
        return _parseBranch(tokens)
    elif op in return_ops:
        return _parseReturn(tokens) # parse after callin convention
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
            regs.append('@' + t)
        elif _isImm(t):
            imms.append(t)
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    if len(regs) < 0:
        raise ParseException("Could not find a variable in tokens: {}".format(tokens))
    if len(imms) == 2:
        # special case of double imms
        op = opcodeParseTable[tokens[0]]
        regs += ['@x0', '@x1']
        return [
            MCInstruction('addi', regs=['@x0', '$zero'], imm=imms[0]),
            MCInstruction('addi', regs=['@x1', '$zero'], imm=imms[1]),
            MCInstruction(op, regs=regs)
        ]
    else:
        imm = None
        if len(imms) != 0:
            imm = imms[0]
        if (imm != None) and (immOpcodeParseTable[tokens[0]] == None):
            return _getImmInstrs(tokens[0], imm=imm, regs=regs)
        elif (imm != None):
            op = immOpcodeParseTable[tokens[0]]
            return [MCInstruction(op, regs=regs, imm=imm)]
        else:
            op = opcodeParseTable[tokens[0]]
            return [MCInstruction(op, regs=regs)]


def _parseAssign(tokens):
    if len(tokens) == 4:
        return _parseArrayAssign(tokens)
    regs = []
    imm = None
    for t in tokens[1:]:
        if _isVar(t):
            regs.append('@' + t)
        elif _isImm(t):
            imm = t
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    if len(regs) < 0:
        raise ParseException("Could not find a variable in tokens: {}".format(tokens))
    if (imm != None) and (immOpcodeParseTable[tokens[0]] == None):
        return _getImmInstrs(tokens[0], imm=imm, regs=regs)
    else:
        op = opcodeParseTable[tokens[0]]
        return [MCInstruction(op, regs=regs)]
    

def _parseArrayAssign(tokens):
    name = '@' + tokens[1]
    size = int(tokens[2]) * 4
    return [
        MCInstruction('li', regs=['$v0'], imm=9),
        MCInstruction('la', regs=['$a0'], imm=size),
        MCInstruction('syscall'),
        MCInstruction('move', regs=[name, '$v0'])
    ]


def _parseGoto(tokens):
    op = opcodeParseTable(tokens[0])
    target = tokens[1]
    return [MCInstruction(op, target=target)]


def _parseBranch(tokens):
    regs = []
    imm = None
    target = tokens[1]
    for t in tokens[2:]: # excludde the target by starting at 2
        if _isVar('@' + t):
            regs.append(t)
        elif _isImm(t):
            imm = t
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    if len(regs) < 0:
        raise ParseException("Could not find a variable in tokens: {}".format(tokens))
    if tokens[0] in ['breq', 'brneq']:
        if imm != None:
            return _getImmInstrs(tokens[0], imm=imm, regs=regs, target=target)
        else:
            op = opcodeParseTable[tokens[0]]
            return [MCInstruction(op, regs=regs, target=target)]
    else:
        instructions = []
        if (imm != None):
            op = 'subi'
            regs = ['@x0'] + regs
            instructions.append(MCInstruction(op, regs=regs, imm=imm))
        else:
            regs = ['@x0'] + regs
            instructions.append(MCInstruction('sub', regs=regs))
        op = opcodeParseTable[tokens[0]]
        instructions.append(MCInstruction(op, regs=['@x0'], target=target))
        return instructions

def _parseReturn(tokens):
    regs = None
    imm = None
    if _isVar(tokens[1]):
        regs = ['@' + tokens[1]]
    elif _isImm(tokens[1]):
        imm = tokens[1]
    else:
        raise ParseException("Failed to parse token: {} of tokens: {}".format(tokens[1], tokens))
    op = opcodeParseTable[tokens[0]]
    if imm != None:
        instructions = []
        instructions.append("--[INSERT CALLING CONVENTION]--"),
        instructions.append(MCInstruction('addi', regs=['@x0', '$zero'], imm=imm))
        instructions.append(MCInstruction('sw', regs=['@x0', '$sp'], offset=0))
        instructions.append(MCInstruction(op, regs=['$ra'])) # this assumes calling convention has loaded the value of $ra
        return instructions
    else:
        instructions = []
        regs.append('$sp')
        instructions.append("--[INSERT CALLING CONVENTION]--"),
        instructions.append(MCInstruction('sw', regs=regs, offset=0))
        instructions.append(MCInstruction(op, regs=['$ra'])) # this assumes calling convention has loaded the value of $ra
        return instructions


def _parseArrayStore(tokens):
    regs = None
    imm = None
    arrayReg = '@' + tokens[2]
    offset = int(tokens[3]) * 4
    if _isVar(tokens[1]):
        regs = ['@' + tokens[1]]
    elif _isImm(tokens[1]):
        imm = tokens[1]
    else:
        raise ParseException("Failed to parse token: {} of tokens: {}".format(tokens[1], tokens))
    op = opcodeParseTable[tokens[0]]
    instructions = []
    if imm != None:   
        instructions.append(MCInstruction('addi', regs=['@x0', '$zero'], imm=imm))
        instructions.append(MCInstruction('sw', regs=['@x0', arrayReg], offset=offset))
        return instructions
    else:
        regs.append(arrayReg)
        instructions.append(MCInstruction('sw', regs=regs, offset=offset))
        return instructions


def _parseArrayLoad(tokens):
    regs = None
    arrayReg = '@' + tokens[2]
    offset = int(tokens[3]) * 4
    regs = ['@' + t for t in tokens[1:3]]
    return [MCInstruction('lw', regs=regs, offset=offset)]


# includes some calling convention
def _parseCall(tokens):
    instructions = []
    op = opcodeParseTable[tokens[0]]
    funcName = tokens[1]
    # save args
    for t in tokens[2:]: # start at first arg
        instructions += _getStackAlloc(1)
        if _isVar(t):
            instructions += _getRegStore('@' + t)
        elif _isImm(t):
            instructions += _getImmStore(t)
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    # jump and link
    instructions.append(MCInstruction(op, target=funcName))
    # pop args
    instructions += _getStackPop(len(tokens) - 2)
    return instructions


# includes some calling convention
def _parseCallr(tokens):
    op = opcodeParseTable[tokens[0]]
    returnReg = '@' + tokens[1]
    funcName = tokens[2]
    instructions = []
    # save args
    for t in tokens[3:]: # start at first arg
        instructions += _getStackAlloc(1)
        if _isVar(t):
            instructions += _getRegStore('@' + t)
        elif _isImm(t):
            instructions += _getImmStore(t)
        else:
            raise ParseException("Failed to parse token: {} of tokens: {}".format(t, tokens))
    # alloc for return value
    instructions += _getStackAlloc(1)
    # jump and link
    instructions.append(MCInstruction(op, target=funcName))
    # pop return value
    instructions += _getRegLoad(returnReg)
    instructions += _getStackPop(1)
    # pop args
    instructions += _getStackPop(len(tokens) - 3)
    return instructions


def _getStackAlloc(amount):
        imm = amount * -4
        return [ MCInstruction('addi', regs=['$sp', '$sp'], imm=imm) ]


def _getImmStore(imm):
    return [
        MCInstruction('addi', regs=['@x0', '$zero'], imm=imm),
        MCInstruction('sw', regs=['@x0', '$sp'], offset=0)
    ]


def _getRegStore(reg):
        return [ MCInstruction('sw', regs=[reg, '$sp'], offset=0) ]


def _getRegLoad(reg):
        return [ MCInstruction('lw', regs=[reg, '$sp'], offset=0) ]


def _getStackPop(amount):
    imm = amount * 4
    return [ MCInstruction('addi', regs=['$sp', '$sp'], imm=imm) ]


def _getImmInstrs(token0, imm=None, regs=None, target=None):
    immSeedInstr = MCInstruction('addi', regs=['@x0', '$zero'], imm=imm)
    op = opcodeParseTable[token0]
    if regs != None:
        regs.append('@x0')
    else:
        regs = ['@x0']
    baseInstr = MCInstruction(op, regs=regs, target=target)
    return [immSeedInstr, baseInstr]


class ParseException(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)

