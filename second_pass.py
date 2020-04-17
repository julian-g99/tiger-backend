from function import Function
from first_pass import is_constant
from mc_function import MCFunction
from typing import Dict, List, Tuple
import re
import copy

from mc_instruction import MCInstruction

def needs_pad(function: MCFunction) -> bool:
    """
    Computes the stack size using given information

    Args:
        function: The MC Function that is being checked

    Returns:
        whether padding is needed
    """
    fp = 1
    arr_length = sum(length for _, length in function.int_arrs)
    ra = 1
    spill_count = len(function.spill_regs)
    saved_count = len(function.saved_regs)
    # arg_count = arg_space(function)
    total = fp + arr_length + spill_count + ra + saved_count

    return total % 2 == 1

def calling_convention(function: MCFunction) -> (List[MCInstruction], List[MCInstruction], Dict[str, int]):
    """
    Handles the callee portion of the calling convention for a particular function. Note that this does not handle any of the caller responsibilities. Those should be handled by the code that deals with `call` and `callr` instructions.

    Currently arrays are always spilled

    Args:
        function: The function whose callee saving and restoring we are doing
        save: Whether we should produce the saving or the restoring code

    Returns:
        A list of MCInstruction
        A dictionary map of spilled virtual register names to its location on the stack
    """
    if not function.has_data:
        return None
    # prologue of the calling convention
    prologue = []
    offsets = {}
    sp = "$sp"
    fp = "$fp"

    # prologue

    # make space for fp and save
    prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
    prologue.append(MCInstruction("sw", regs=[fp, sp], offset=0))
    prologue.append(MCInstruction("move", regs=[fp, sp]))

    # make space for array
    curr_offset = -4
    for arr in function.int_arrs:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-arr[1]*4)) # arr[1] should the size
        offsets[arr[0]] = curr_offset
        curr_offset -= arr[1] * 4

    # make space for local variables
    if len(function.spill_regs) != 0:
        for val in function.int_vals:
            prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
            offsets[val] = curr_offset
            curr_offset -= 4

    # padding
    if needs_pad(function):
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        curr_offset -= 4

    # return address
    prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
    prologue.append(MCInstruction("sw", regs=["$ra", sp], offset=0))

    # s registers
    for s in function.saved_regs:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        prologue.append(MCInstruction("sw", regs=[s, sp], offset=0)) # TODO: check if this is how the mc function is filled
        offsets[s] = curr_offset
        curr_offset -= 4


    # epilogue
    epilogue = []

    # restore the s registers
    for s in function.saved_regs[::-1]:
        epilogue.append(MCInstruction("lw", regs=[s, sp], offest=0))
        epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    # restore the return address
    epilogue.append(MCInstruction("sw", regs=["$ra", sp], offset=0))
    epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    # skip over padding if it's there
    if needs_pad(function):
        epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    # tear down the local variables
    if len(function.spill_regs) != 0:
        spill_count = len(function.spill_regs)
        epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4*spill_count))

    # tear down the array
    for arr in function.int_arrs:
        epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=arr[1]*4))

    # restore the fp
    epilogue.append(MCInstruction("lw", regs=[fp, sp], offset=0))
    epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    return prologue, epilogue, offsets


def spill(spill_count: int, reg_map: Dict[str, str], ir_regs: [str], offsets: Dict[str, int], load: bool) -> (List[MCInstruction], Dict[str, str]):
    """
    Performs spilling given a register map and the set of original virtual registers, with some additional information. At the end, outputs the spilling code as well as the complete register mapping (with every virtual register mapped to a physical register). Uses t0-t2 for spilling (since a single instruction should not have more than three registers).

    Args:
        spill_count: the number of values to be spilled
        reg_map: the register mapping given by the allocator
        ir_regs: the original (virtual) registers of the instruction
        offsets: the map from virtual register to the frame pointer offset on the stack
        load: whether this is for loading or storing

    Returns:
        output: a list of MCInstructions which is the spill load/store code
        reg_map: a new register map such that anything which was spilled is replaced by a temp register.
    """
    # NOTE: it's assumed that the position at $fp will be used for saving the register used here
    assert(spill_count <= 3)

    if load:
        op = "lw"
    else:
        op = "sw"

    # spill_regs = [k for (k, v) in reg_map if v == "spill"]  # TODO: double check this
    output = []
    # m = {}

    curr_temp = 0
    # for phys, ir in zip(phys_reg, ir_regs):
    for ir, phys in reg_map.items():
        if phys == "spill":
            output.append(MCInstruction(op, regs=["$t%d"%curr_temp, "$fp"], offset=offsets[ir]))
            reg_map[ir] = "$t%d" % curr_temp
            curr_temp += 1

    return output, reg_map

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

def convert_intrinsic(instr: MCInstruction) -> List[MCInstruction]:
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
    op = instr.op
    if op == "geti" or op == "getc": # CHECK: does getc and geti actually work in the same way?
        dest = instr.dest

        # saving v0
        save, restore = save_and_restore("$v0")
        output += save

        # moving syscode into v0
        output.append(MCInstruction("move", regs=["$v0"], imm=sys_codes["read_int"]))

        # syscall
        output.append(MCInstruction("syscall"))

        # moving output into destination
        output.append(MCInstruction("move", regs=[dest, "$v0"]))

        # restoring v0
        output += restore
    elif op == "getf":
        raise NotImplementedError("getf() isn't implemented as floats are not supported")
    elif op == "puti":
        arg = instr.arguments[0]

        # saving a0 and v0
        save_a0, restore_a0 = save_and_restore("$a0")
        save_v0, restore_v0 = save_and_restore("$v0")
        output += save_a0
        output += save_v0

        # moving argument into a0
        if is_constant(arg):
            output.append(MCInstruction("move", regs=["$a0"], imm=arg))
        else:
            output.append(MCInstruction("move", regs=["$a0", arg]))

        # moving syscode into v0
        output.append(MCInstruction("move", regs=["$v0"], imm=sys_codes["print_int"]))

        # syscall
        output.append(MCInstruction("syscall"))

        # restoring a0 and v0
        output += restore_v0
        output += restore_a0
    elif op == "putf":
        raise NotImplementedError("putf() isn't implemented as floats are not supported")
    elif op == "putc":
        arg = instr.arguments[0]

        # saving a0 and v0
        save_a0, restore_a0 = save_and_restore("$a0")
        save_v0, restore_v0 = save_and_restore("$v0")
        output += save_a0
        output += save_v0

        # moving argument into a0
        if is_constant(arg):
            output.append(MCInstruction("move", regs=["$a0"], imm=arg))
        else:
            output.append(MCInstruction("move", regs=["$a0", arg]))

        # moving syscode into v0
        output.append(MCInstruction("move", regs=["$v0"], imm=sys_codes["print_char"]))

        # syscall
        output.append(MCInstruction("syscall"))

        # restoring a0 and v0
        output += restore_v0
        output += restore_a0
    else:
        raise ValueError("Unexpected intrinsic function")


def convert_instr(reg_map, instr: MCInstruction, offsets: Dict[str, int]) -> List[MCInstruction]:
    # TODO: assume the caller's stack is already even, add padding if the number of args that need to be passed through the stack is odd
    output = []
    # count the number of arguments
    num_args = len(instr.arguments)
    if num_args <= 4:
        curr_reg = 0
        for arg in instr.arguments:
            arg_reg = "$a%d" % curr_reg
            curr_reg += 1
            # TODO: cases to consider:
                # 1. arg is immediate value
                # 2. arg is in a physical register
                # 3. arg is on the stack as a local variable (i.e., it's spilled)
                # 4. arg is on the stack as an array value
            # FIXME: using the cases above, move the value of arg into arg_reg
    else:
        curr_reg = 0
        for i in range(4):
            # TODO: do the same as above
            arg_reg = "%a%d" % curr_reg
            curr_reg += 1

        # TODO: store the rest on the stack

    # NOTE: this if is at this level because the args and dests still need to be translated to physical registers first
    if instr.op != "callr" and instr.op != "call":
        intrinsics = ["geti", "getf", "getc", "puti", "putf", "putc"]
        if instr.name in intrinsics:
            convert_intrinsic(instr)
        output = []

        spill_count = list(reg_map.values()).count("spill")

        if spill_count != 0:
            spill_load, spill_map = spill(spill_count, reg_map, instr.regs, offsets, load=True)
            output += spill_load
            # for i in range(len(copy.regs)):
                # if copy.regs[i] == "spill":
                    # copy.regs[i] = spill_map[orig_regs[i]]
            new_regs = [spill_map[r] for r in instr.regs]

            spill_store, _ = spill(spill_count, reg_map, instr.regs, offsets, load=False)

    return output

def translate_body(function: MCFunction):
    # for bb in function.bbs:
        # for instr in bb:
            # # FIXME: change this to actually translate the function, might want to refactor convert_instr first

    return function.body

def parse_function(function: MCFunction):
    # print(reg_map)
    assert(len(function.reg_maps) == len(function.bbs))

    # prologue = get_prologue(function)
    prologue, epilogue, offsets = calling_convention(function)
    #NOTE: if the return value above is None that means it's a simple leaf
    translated_body = translate_body(function)

    res = prologue + translated_body + epilogue

    for i in prologue:
        print(i)
    print()
    for i in translated_body:
        print(i)
    print()
    for i in epilogue:
        print(i)

    return res

def test():
    i = 0 # using this as nop


if __name__ == "__main__":
    test()
