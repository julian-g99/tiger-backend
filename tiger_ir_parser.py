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
        return _parseReturn(tokens)
    elif op in call_ops:
        return line
    elif op in callr_ops:
        return line
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


def _parseBinary(tokens):
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
            regs.append(t)
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
    name = tokens[1]
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
        if _isVar(t):
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
            regs = ['$x'] + regs
            instructions.append(MCInstruction(op, regs=regs, imm=imm))
        else:
            regs = ['$x'] + regs
            instructions.append(MCInstruction('sub', regs=regs))
        op = opcodeParseTable[tokens[0]]
        instructions.append(MCInstruction(op, regs=['$x'], target=target))
        return instructions

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
        instructions = []
        instructions.append(MCInstruction('addi', regs=['$x', '$zero'], imm=imm))
        instructions.append(MCInstruction('sw', regs=['$x', '$sp'], offset=0))
        instructions.append(MCInstruction(op, regs=['$ra'])) # this assumes calling convention has loaded the value of $ra
        return instructions
    else:
        instructions = []
        regs.append('$sp')
        instructions.append(MCInstruction('sw', regs=regs, offset=0))
        instructions.append(MCInstruction(op, regs=['$ra'])) # this assumes calling convention has loaded the value of $ra
        return instructions


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
    op = opcodeParseTable[tokens[0]]
    instructions = []
    if imm != None:   
        instructions.append(MCInstruction('addi', regs=['$x', '$zero'], imm=imm))
        instructions.append(MCInstruction('sw', regs=['$x', arrayReg], offset=offset))
        return instructions
    else:
        regs.append(arrayReg)
        instructions.append(MCInstruction('sw', regs=regs, offset=offset))
        return instructions


def _parseArrayLoad(tokens):
    regs = None
    arrayReg = tokens[2]
    offset = int(tokens[3]) * 4
    regs = tokens[1:3]
    return [MCInstruction('lw', regs=regs, offset=offset)]


def _getImmInstrs(token0, imm=None, regs=None, target=None):
    immSeedInstr = MCInstruction('addi', regs=['$x', '$zero'], imm=imm)
    op = opcodeParseTable[token0]
    if regs != None:
        regs.append('$x')
    else:
        regs = ['$x']
    baseInstr = MCInstruction(op, regs=regs, target=target)
    return [immSeedInstr, baseInstr]


class ParseException(Exception):
    def __init__(self, msg):
        super().__init__(self, msg)

