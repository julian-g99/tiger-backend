from ir_instruction import IRInstruction
from function import Function
from mc_instruction import MCInstruction
from parser import parse_instructions
from symbolic_map import SymbolicMap
import re

from typing import List

s_map = SymbolicMap()

def is_constant(arg: str) -> bool:
    pattern = r'^-?\d+.?\d*$'
    return bool(re.compile(pattern).search(arg))

def find_functions(instructions: List[IRInstruction]) -> List[List[IRInstruction]]:
    output = []

    inside_function = False
    curr_function = []
    for instr in instructions:
        if instr.instruction_type == "function_start":
            inside_function = True
            curr_function = []
            curr_function.append(instr)
        elif instr.instruction_type == "function_end":
            curr_function.append(instr)
            inside_function = False
            output.append(Function(curr_function))
        else:
            curr_function.append(instr)

    return output


def convert_arithmetic(instr: IRInstruction) -> str:
    """
    Converts an arithmetic instruction to assembly
    """
    assert(instr.is_arithmetic())
    assert(not is_constant(instr.argument_list[0]))

    global s_map

    dest, src0, src1 = instr.argument_list
    output = []
    if instr.instruction_type == "add" or instr.instruction_type == "sub":
        if not is_constant(src0) and not is_constant(src1):
            # neither is constant
            output.append(MCInstruction(instr.instruction_type, regs=[s_map[dest], s_map[src0], s_map[src1]]))
        elif not is_constant(src0) and is_constant(src1):
            # src1 is constant
            output.append(MCInstruction(instr.instruction_type+'i', regs=[s_map[dest], s_map[src0]], imm=src1))
        elif is_constant(src0) and not is_constant(src1):
            # src0 is constant
            output.append(MCInstruction(instr.instruction_type+'i', regs=[s_map[dest], s_map[src1]], imm=src0))
        else:
            # both are constant
            output.append(MCInstruction("move", regs=['zero']))
            output.append(MCInstruction("addi", regs=[s_map[src0]]))
            output.append(MCInstruction(instr.instruction_type+'i', regs=[s_map[dest], s_map[src1]]))
    if instr.instruction_type == "mult":
        # FIXME: currently assumes the result will be 32 bit
        if not is_constant(src0) and not is_constant(src1):
            # neither is constant
            # output = "mult %s, %s\n" % (s_map[src0], s_map[src1])
            output.append(MCInstruction("mult", regs=[s_map[src0], s_map[src1]]))
        elif not is_constant(src0) and is_constant(src1):
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src1))
            output.append(MCInstruction("mult", regs=[s_map[src0], s_map[dest]]))
        elif is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src0))
            output.append(MCInstruction("mult", regs=[s_map[src1], s_map[dest]]))
        else:
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src0))
            output.append(MCInstruction("addi", regs=[s_map["multiply_temporary_register"], "zero"], imm=src1))
            output.append(MCInstruction("mult", regs=[s_map[dest], s_map["multiply_temporary_register"]]))
        output.append(MCInstruction("mflo", regs=[s_map[dest]]))
    if instr.instruction_type == "div":
        # FIXME: currently only keeps the integer quotient
        if not is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction("div", regs=[s_map[src0], s_map[src1]]))
        elif not is_constant(src0) and is_constant(src1):
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src1))
            output.append(MCInstruction("div", regs=[s_map[src1], s_map[dest]]))
        elif is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src0))
            output.append(MCInstruction("div", regs=[s_map[src1], s_map[dest]]))
        else:
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src0))
            output.append(MCInstruction("addi", regs=[s_map["division_temporary_register"], "zero"], imm=src1))
            output.append(MCInstruction("div", regs=[s_map[dest], s_map["division_temporary_register"]]))
        output.append(MCInstruction("mflo", regs=[s_map[dest]]))
    if instr.instruction_type in ["and", "or"]:
        i_type = instr.instruction_type
        if not is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction(i_type, regs=[s_map[dest], s_map[src0], s_map[src1]]))
        elif not is_constant(src0) and is_constant(src1):
            output.append(MCInstruction(i_type+"i", regs=[s_map[dest], s_map[src0]], imm=src1))
        elif is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction(i_type+"i", regs=[s_map[dest], s_map[src1]], imm=src0))
        else:
            output.append(MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src0))
            output.append(MCInstruction(i_type+"i", regs=[s_map[dest], s_map[dest]], imm=src1))

    return output

def convert_assignment(instr: IRInstruction) -> str:
    dest, src = instr.argument_list
    assert(instr.instruction_type == "val_assign")
    assert(not is_constant(dest))
    
    if not is_constant(src):
        output = [MCInstruction("move", regs=[s_map[dest], s_map[src]])]
    else:
        output = [MCInstruction("addi", regs=[s_map[dest], "zero"], imm=src)]

    return output

def convert_branch(instr: IRInstruction) -> str:
    if instr.instruction_type == "goto":
        target = instr.argument_list[0]
        return [MCInstruction("j", target=target)]
    else:
        branch_map = {"breq": "beq", "brneq": "bne",
                      "brlt": "blt", "brgt": "bgt",
                      "brgeq": "bge", "brleq": "ble"}
        label, src0, src1 = instr.argument_list
        op = branch_map[instr.instruction_type]

        return [MCInstruction(op, regs=[s_map[src0], s_map[src1]], target=label)]

def convert_array_load_store(instr):
    # TODO: implement
    assert(instr.instruction_type in ["array_store", "array_load"])
    assert(len(instr.argument_list) == 3)
    val, array, index = instr.argument_list
    array = s_map[array]
    output = []

    if instr.instruction_type == "array_load":
        op = "lw"
    else:
        op = "sw"


    if is_constant(index) and not is_constant(val):
        output.append(MCInstruction(op, regs=[s_map[val], s_map[array]], offset=index))
    elif is_constant(index) and is_constant(val):
        output.append(MCInstruction("addi", regs=[s_map["array_store_temp_reg"], "zero"], imm=val))
        output.append(MCInstruction(op, regs=[s_map["array_store_temp_reg"], array], offset=index))
        del s_map["array_store_temp_reg"]
    elif not is_constant(index) and is_constant(val):
        # getting the immediate value into a register
        output.append(MCInstruction("addi", regs=[s_map["array_store_temp_reg0", "zero"]], imm=val))

        # address calculation
        output.append(MCInstruction("add", regs=[array, array, s_map[index]]))
        output.append(MCInstruction(op, regs=[s_map["array_store_temp_reg"], array]))
        del s_map["array_store_temp_reg"]
        output.append(MCInstruction("sub", regs=[array, array, s_map[index]]))
    else:
        output.append(MCInstruction("add", regs=[array, array, s_map[index]]))
        output.append(MCInstruction(op, regs=[s_map[val], array]))
        output.append(MCInstruction("sub", regs=[array, array, s_map[index]]))
    return output


def convert_array_assign(instr):
    # TODO: implement
    assert(instr.instruction_type == "array_assign")
    assert(len(instr.argument_list) == 3)
    array, size, value = instr.argument_list

    temp0 = s_map["array_assign_temp0"]
    temp1 = s_map["array_assign_temp1"]
    temp2 = s_map["array_assign_temp2"]

    output = []

    if is_constant(size) and is_constant(value):
        output.append(MCInstruction("move", regs=[temp0, array]))
        output.append(MCInstruction("addi", regs=[temp1, temp0], imm=size))
        output.append(MCInstruction("li", regs=[temp2], imm=value))

        output.append(MCInstruction("label", target="CONVERT_ARRAY_ASSIGN_LOOP"))
        output.append(MCInstruction("bge",regs=[temp0, temp1], target="CONVERT_ARRAY_ASSIGN_END"))
        output.append(MCInstruction("sw", regs=[temp2, temp0]))
        output.append(MCInstruction("addi", regs=[temp0, temp0], imm=4))
        output.append(MCInstruction("j", target="CONVERT_ARRAY_ASSIGN_LOOP"))
    elif is_constant(size) and not is_constant(value):
        output.append(MCInstruction("move", regs=[temp0, array]))
        output.append(MCInstruction("add", regs=[temp1, temp0, size]))

        output.append(MCInstruction("label", target="CONVERT_ARRAY_ASSIGN_LOOP"))
        output.append(MCInstruction("bge",regs=[temp0, temp1], target="CONVERT_ARRAY_ASSIGN_END"))
        output.append(MCInstruction("sw", regs=[value, temp0]))
        output.append(MCInstruction("addi", regs=[temp0, temp0], imm=4))
        output.append(MCInstruction("j", target="CONVERT_ARRAY_ASSIGN_LOOP"))
    elif not is_constant(size) and is_constant(value):
        output.append(MCInstruction("move", regs=[temp0, array]))
        output.append(MCInstruction("add", regs=[temp1, temp0, size]))
        output.append(MCInstruction("li", regs=[temp2], imm=value))

        output.append(MCInstruction("label", target="CONVERT_ARRAY_ASSIGN_LOOP"))
        output.append(MCInstruction("bge",regs=[temp0, temp1], target="CONVERT_ARRAY_ASSIGN_END"))
        output.append(MCInstruction("sw", regs=[temp2, temp0]))
        output.append(MCInstruction("addi", regs=[temp0, temp0], imm=4))
        output.append(MCInstruction("j", target="CONVERT_ARRAY_ASSIGN_LOOP"))
    else:
        output.append(MCInstruction("move", regs=[temp0, array]))
        output.append(MCInstruction("add", regs=[temp1, temp0, size]))

        output.append(MCInstruction("label", target="CONVERT_ARRAY_ASSIGN_LOOP"))
        output.append(MCInstruction("bge",regs=[temp0, temp1], target="CONVERT_ARRAY_ASSIGN_END"))
        output.append(MCInstruction("sw", regs=[value, temp0]))
        output.append(MCInstruction("addi", regs=[temp0, temp0], imm=4))
        output.append(MCInstruction("j", target="CONVERT_ARRAY_ASSIGN_LOOP"))

    del s_map["array_assign_temp0"]
    del s_map["array_assign_temp1"]
    del s_map["array_assign_temp2"]

    return output

def function_to_asm(function: Function) -> List[MCInstruction]:

    # prologue
    prologue = []
    sp = "$sp"
    if function.stack_type == "simple_leaf":
        prologue += function.body
    elif function.stack_type == "data_leaf":
        # make space for array
        curr_offset = 0
        if function.has_array:
            for arr in function.int_arrs:
                prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=arr[1]*4)) #arr[1] should be the size of the array
                curr_offset += arr[1]
                # FIXME: give the array address to something (probably a map?)

        # add padding if needed
        if curr_offset + function.saved_regs_count % 2 == 1:
            prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=4))

        # store any saved registers that we will change
        prologue.append(MCInstruction("addiu", regs=["$sp", "$sp"], offset=function.saved_regs_count * 4))
        curr_offset += function.saved_regs_count # NOTE: this is only for keep track of double-words
        for i in range(function.saved_regs_count):
            prologue.append(MCInstruction("sw", regs=["$sp", "$sp"], offset=i*4))
    elif function.stack_type == "nonleaf":
        # TODO: implement
        a = 0



    # body
    body = []
    for i in function.body:
        body += instr_to_asm(body)

    #epilogue
    epilogue = []
    sp = "$sp"
    if function.stack_type == "simple_leaf":
        epilogue.append(MCInstruction("jr", regs="$ra"))

def convert_label(instr: IRInstruction):
    assert(instr.instruction_type == "label")
    return [MCInstruction("label", target=instr.argument_list[0])]

def convert_calls(instr: IRInstruction):
    # NOTE: this is temporary and should not ever end up in the final output
    assert(instr.instruction_type == "call" or instr.instruction_type == "callr")
    if instr.instruction_type == "call":
        function_name = instr.argument_list[0]
        arguments = instr.argument_list[1:]
        return MCInstruction("call", function_name=function_name, arguments=arguments)
    else:
        return_dest = instr.argument_list[0]
        function_name = instr.argument_list[1]
        arguments = instr.argument_list[2:]
        return MCInstruction("callr", return_dest=return_dest, function_name=function_name, arguments=arguments)



def instr_to_asm(instr: IRInstruction) -> List[IRInstruction]:
    """
    Converts an IRInstruction object into assembly code string
    Curretnly uses only symbolic registers
    """

    if instr.is_arithmetic():
        assert(not is_constant(instr.argument_list[0])) # dest can't be constant
        return convert_arithmetic(instr)
    elif instr.instruction_type == "val_assign":
        return convert_assignment(instr)
    elif instr.is_branch:
        return convert_branch(instr)
    elif instr.instruction_type == "array_store" or instr.instruction_type == "array_load":
        return convert_array_load_store(instr)
    elif instr.instruction_type == "array_assign":
        return convert_array_assign(instr)
    elif instr.instruction_type == "label":
        return convert_label(instr)
    elif instr.instruction_type in ["call", "callr"]:
        return convert_calls(instr)

def main():
    instructions = parse_instructions("./test_cases/bfs/bfs/ir")
    functions = find_functions(instructions)
    output = []
    for f in functions:
        output += function_to_asm(f)

    # FIXME: refactor this to output to a file instead of returning
    return output

if __name__ == "__main__":
    main()
