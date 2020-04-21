from ir_instruction import IRInstruction
from function import Function
from mc_instruction import MCInstruction
from parser import parse_instructions
from symbolic_map import SymbolicMap
import re

from typing import List, Tuple

s_map = SymbolicMap()

def is_constant(arg: str) -> bool:
    pattern = r'^-?\d+.?\d*$'
    return bool(re.compile(pattern).search(arg))

def find_functions(instructions: List[IRInstruction]) -> List[List[IRInstruction]]:
    output = []

    inside_function = False
    curr_function = []
    curr_name = None
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
            output.append(MCInstruction(instr.instruction_type, regs=[dest, src0, src1]))
        elif not is_constant(src0) and is_constant(src1):
            # src1 is constant
            src1 = int(src1)
            if instr.instruction_type == "add":
                output.append(MCInstruction("addi", regs=[dest, src0], imm=src1))
            else:
                output.append(MCInstruction("addi", regs=[dest, src0], imm=-src1))
        elif is_constant(src0) and not is_constant(src1):
            # src0 is constant
            src = int(src0)
            if instr.instruction_type == "add":
                output.append(MCInstruction("addi", regs=[dest, src1], imm=src0))
            else:
                output.append(MCInstruction("li", regs=[dest], imm=src0))
                output.append(MCInstruction("sub", regs=[dest], imm=src1))
        else:
            # both are constant
            src1 = int(src1)
            src0 = int(src0)
            output.append(MCInstruction("li", regs=[dest], imm=src0))
            if instr.instruction_type == "add":
                output.append(MCInstruction("addi", regs=[dest], imm=src1))
            else:
                output.append(MCInstruction("addi", regs=[dest], imm=-src1))
    if instr.instruction_type == "mult":
        # FIXME: currently assumes the result will be 32 bit
        if not is_constant(src0) and not is_constant(src1):
            # neither is constant
            # output = "mult %s, %s\n" % (src0, src1)
            output.append(MCInstruction("mult", regs=[src0, src1]))
        elif not is_constant(src0) and is_constant(src1):
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src1))
            output.append(MCInstruction("mult", regs=[src0, dest]))
        elif is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src0))
            output.append(MCInstruction("mult", regs=[src1, dest]))
        else:
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src0))
            output.append(MCInstruction("addi", regs=[s_map["multiply_temporary_register"], "$0"], imm=src1))
            output.append(MCInstruction("mult", regs=[dest, s_map["multiply_temporary_register"]]))
        output.append(MCInstruction("mflo", regs=[dest]))
    if instr.instruction_type == "div":
        # FIXME: currently only keeps the integer quotient
        if not is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction("div", regs=[src0, src1]))
        elif not is_constant(src0) and is_constant(src1):
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src1))
            output.append(MCInstruction("div", regs=[src1, dest]))
        elif is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src0))
            output.append(MCInstruction("div", regs=[src1, dest]))
        else:
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src0))
            output.append(MCInstruction("addi", regs=[s_map["division_temporary_register"], "$0"], imm=src1))
            output.append(MCInstruction("div", regs=[dest, s_map["division_temporary_register"]]))
        output.append(MCInstruction("mflo", regs=[dest]))
    if instr.instruction_type in ["and", "or"]:
        i_type = instr.instruction_type
        if not is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction(i_type, regs=[dest, src0, src1]))
        elif not is_constant(src0) and is_constant(src1):
            output.append(MCInstruction(i_type+"i", regs=[dest, src0], imm=src1))
        elif is_constant(src0) and not is_constant(src1):
            output.append(MCInstruction(i_type+"i", regs=[dest, src1], imm=src0))
        else:
            output.append(MCInstruction("addi", regs=[dest, "$0"], imm=src0))
            output.append(MCInstruction(i_type+"i", regs=[dest, dest], imm=src1))

    return output

def convert_assignment(instr: IRInstruction) -> str:
    dest, src = instr.argument_list
    assert(instr.instruction_type == "val_assign")
    assert(not is_constant(dest))
    
    if not is_constant(src):
        output = [MCInstruction("move", regs=[dest, src])]
    else:
        output = [MCInstruction("li", regs=[dest], imm=src)]

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

        return [MCInstruction(op, regs=[src0, src1], target=label)]

def convert_array_load_store(instr):
    # TODO: implement
    assert(instr.instruction_type in ["array_store", "array_load"])
    assert(len(instr.argument_list) == 3)
    val, array, index = instr.argument_list
    array = array
    output = []

    if instr.instruction_type == "array_load":
        op = "lw"
    else:
        op = "sw"


    if is_constant(index) and not is_constant(val):
        output.append(MCInstruction(op, regs=[val, array], offset=index))
    elif is_constant(index) and is_constant(val):
        output.append(MCInstruction("addi", regs=[s_map["array_store_temp_reg"], "$0"], imm=val))
        output.append(MCInstruction(op, regs=[s_map["array_store_temp_reg"], array], offset=index))
        del s_map["array_store_temp_reg"]
    elif not is_constant(index) and is_constant(val):
        # getting the immediate value into a register
        output.append(MCInstruction("addi", regs=[s_map["array_store_temp_reg0", "$0"]], imm=val))

        # address calculation
        output.append(MCInstruction("add", regs=[array, array, index]))
        output.append(MCInstruction(op, regs=[s_map["array_store_temp_reg"], array]))
        del s_map["array_store_temp_reg"]
        output.append(MCInstruction("sub", regs=[array, array, index]))
    else:
        output.append(MCInstruction("add", regs=[array, array, index]))
        output.append(MCInstruction(op, regs=[val, array]))
        output.append(MCInstruction("sub", regs=[array, array, index]))
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

def convert_label(instr: IRInstruction):
    assert(instr.instruction_type == "label")
    return [MCInstruction("label", target=instr.argument_list[0])]

def save_and_restore(reg_name: str) -> Tuple[List[MCInstruction], List[MCInstruction]]:
    """
    Computes the save and restore code for a single register.
    Args:
        - reg_name: the register to be saved and restored, make sure this is a physical register
    Returns:
        - a tuple of list of instructions. The first of which is the save code, the second is the restore code
    """
    save_code = []
    restore_code = []
    sp = "$sp"

    save_code.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
    save_code.append(MCInstruction("sw", regs=[reg_name, sp], offset=0))

    restore_code.append(MCInstruction("lw", regs=[reg_name, sp], offset=0))
    restore_code.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    return save_code, restore_code

def convert_intrinsic(instr: IRInstruction, name: str, args: List[str], dest: str=None) -> List[MCInstruction]:
    """
    Converts an intrinsic function call to use the relevant syscall. Note that v0 and a0 is always saved and restored, regardless of whether these registers are actually used in the function.
    
    Args:
        - instr: the instruction to be translated
    Returns:
        - a list of instructions equivalent to the intrinsic function
    """
    sys_codes = {"print_int": 1,
                "print_float": 2,
                "print_double": 3,
                "print_string": 4,
                "read_int": 5,
                "raed_float": 6,
                "read_double": 7,
                "read_string": 8,
                "sbrk": 9,
                "exit": 10,
                "print_char": 11}
    output = []
    op = name
    if op == "geti" or op == "getc": # CHECK: does getc and geti actually work in the same way?
        # saving v0, CHECK: is this really needed?
        # save, restore = save_and_restore("$v0")
        # output += save

        # moving syscode into v0
        output.append(MCInstruction("li", regs=["$v0"], imm=sys_codes["read_int"]))

        # syscall
        output.append(MCInstruction("syscall"))

        # moving output into destination
        output.append(MCInstruction("move", regs=[dest, "$v0"]))

        # restoring v0
        # output += restore
        return output
    elif op == "getf":
        raise NotImplementedError("getf() isn't implemented as floats are not supported")
    elif op == "puti":
        # arg = instr.arguments[0]
        arg = args[0]

        # saving a0 and v0
        # save_a0, restore_a0 = save_and_restore("$a0")
        # save_v0, restore_v0 = save_and_restore("$v0")
        # output += save_a0
        # output += save_v0

        # moving argument into a0
        if is_constant(arg):
            output.append(MCInstruction("li", regs=["$a0"], imm=arg))
        else:
            output.append(MCInstruction("move", regs=["$a0", arg]))

        # moving syscode into v0
        output.append(MCInstruction("li", regs=["$v0"], imm=sys_codes["print_int"]))

        # syscall
        output.append(MCInstruction("syscall"))

        # restoring a0 and v0
        # output += restore_v0
        # output += restore_a0
        return output
    elif op == "putf":
        raise NotImplementedError("putf() isn't implemented as floats are not supported")
    elif op == "putc":
        # arg = instr.arguments[0]
        arg = args[0]

        # saving a0 and v0
        # save_a0, restore_a0 = save_and_restore("$a0")
        # save_v0, restore_v0 = save_and_restore("$v0")
        # output += save_a0
        # output += save_v0

        # moving argument into a0
        if is_constant(arg):
            output.append(MCInstruction("li", regs=["$a0"], imm=arg))
        else:
            output.append(MCInstruction("move", regs=["$a0", arg]))

        # moving syscode into v0
        output.append(MCInstruction("li", regs=["$v0"], imm=sys_codes["print_char"]))

        # syscall
        output.append(MCInstruction("syscall"))

        # restoring a0 and v0
        # output += restore_v0
        # output += restore_a0
        return output
    else:
        raise ValueError("Unexpected intrinsic function: %s" % op)



def convert_calls(instr: IRInstruction):
    # NOTE: this is temporary and should not ever end up in the final output
    assert(instr.instruction_type == "call" or instr.instruction_type == "callr")
    intrinsics = ["geti", "getf", "getc", "puti", "putf", "putc"]
    sp = "$sp"
    if instr.instruction_type == "call":
        function_name = instr.argument_list[0]
        arguments = instr.argument_list[1:]
        return_dest = None
    else:
        return_dest = instr.argument_list[0]
        function_name = instr.argument_list[1]
        arguments = instr.argument_list[2:]

    if function_name in intrinsics:
        return convert_intrinsic(instr, function_name, arguments, return_dest)

    output = []
    # normal function call
    first_section = arguments[:4]
    for i, arg in enumerate(first_section):
        arg_reg = "$a%d" % i
        if is_constant(arg):
            output.append(MCInstruction("li", regs=[arg_reg], imm=arg))
        else:
            output.append(MCInstruction("move", regs=[arg_reg, arg]))

    second_section = arguments[4:][:-1] # pushing in reverse order
    temp = s_map["CONVERT_CALLS_TEMP_REG"]
    stack_length = 0
    for arg in second_section:
        output.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        stack_length += 1
        if is_constant(arg):
            output.append(MCInstruction("li", regs=[temp], imm=arg))
            output.append(MCInstruction("sw", regs=[temp, sp], imm=0))
        else:
            output.append(MCInstruction("sw", regs=[arg, sp], imm=0))
    del s_map["CONVERT_CALLS_TEMP_REG"]
    # paddding
    if len(second_section) % 2 == 1:
        output.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        stack_length += 1

    # the actual call itself
    output.append(MCInstruction("jal", target=function_name))

    if instr.instruction_type == "callr":
        # reading the return value
        output.append(MCInstruction("move", regs=[return_dest, "$v0"])) # shouldn't have anything that doesn't fit in one word

    # popping the stack
    if stack_length != 0:
        output.append(MCInstruction("addiu", regs=[sp, sp], imm=4*stack_length))

    return output

def convert_return(instr):
    assert(instr.instruction_type == "return")
    assert(len(instr.argument_list) == 1)
    ret_val = instr.argument_list[0]
    output = []
    v0 = "$v0"
    if is_constant(ret_val):
        output.append(MCInstruction("li", regs=[v0], imm=ret_val))
    else:
        output.append(MCInstruction("move", regs=[v0, ret_val]))

    return output

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
    elif instr.instruction_type == "return":
        return convert_return(instr)

# def main():
    # instructions = parse_instructions("./test_cases/bfs/bfs/ir")
    # functions = find_functions(instructions)
    # output = []
    # for f in functions:
        # output += function_to_asm(f)

    # # FIXME: refactor this to output to a file instead of returning
    # return output

# if __name__ == "__main__":
    # main()
