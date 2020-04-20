from function import Function
from first_pass import is_constant
from mc_function import MCFunction
from typing import Dict, List, Tuple
import re
import copy

from mc_instruction import MCInstruction

def needs_pad(function: MCFunction) -> bool:
    """
    Computes the stack size using given information and returns whether padding is needed (since sp needs to be a multiple of 8)

    Args:
        function: The MC Function that is being checked

    Returns:
        whether padding is needed
    """
    fp = 1
    arr_length = sum(length for _, length in function.int_arrs)
    ra = 1
    # spill_count = len(function.spill_regs)
    # saved_count = len(function.saved_regs)
    # arg_count = arg_space(function)
    num_vars = function.num_vars
    # total = fp + arr_length + spill_count + ra + saved_count
    total = fp + ra + arr_length + num_vars

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

    # make space for arrays
    curr_offset = -4
    for arr in function.int_arrs:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-arr[1]*4)) # arr[1] should the size
        offsets[arr[0]] = curr_offset
        curr_offset -= arr[1] * 4

    # make space for local variables
    # for greedy local alloc, need to save everything (even non-spilled)
    for val in function.int_vals:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        offsets[val] = curr_offset
        curr_offset -= 4

    # save all the t registers (as specified in the pdf)
    for i in range(8):
        t_reg = "$t%d" % i
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        prologue.append(MCInstruction("sw", regs=[t_reg, sp], imm=0))
        offsets[t_reg] = curr_offset
        curr_offset -= 4

    # padding
    if needs_pad(function):
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        curr_offset -= 4

    # return address
    prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
    prologue.append(MCInstruction("sw", regs=["$ra", sp], offset=0))
    offsets["$ra"] = curr_offset
    curr_offset -= 4

    # s registers
    for s in function.saved_regs:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        prologue.append(MCInstruction("sw", regs=[s, sp], offset=0))
        offsets[s] = curr_offset
        curr_offset -= 4


    # epilogue
    epilogue = []

    # restore the s registers
    # for s in function.saved_regs[::-1]:
    for s in function.saved_regs:
        epilogue.append(MCInstruction("lw", regs=[s, fp], offset=offsets[s]))

    # restore the return address
    epilogue.append(MCInstruction("lw", regs=["$ra", sp], offset=offsets["$ra"]))
    # epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    # restore t registers
    for i in range(8):
        t_reg = "$t%d" % i
        epilogue.append(MCInstruction("lw", regs=[t_reg, fp], offset=offsets[t_reg]))

    # skip over padding if it's there
    # if needs_pad(function):
        # epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    # tear down the local variables
    # if len(function.spill_regs) != 0:
        # spill_count = len(function.spill_regs)
        # epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4*spill_count))

    # tear down the array
    # for arr in function.int_arrs:
        # epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=arr[1]*4))

    # restore the fp
    epilogue.append(MCInstruction("move", regs=[sp, fp])) # moving sp back to fp
    epilogue.append(MCInstruction("lw", regs=[fp, sp], offset=0))
    epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    return prologue, epilogue, offsets


def spill(reg_map: Dict[str, str], instr: MCInstruction, offsets: Dict[str, int]) -> (List[MCInstruction], List[MCInstruction], Dict[str, str]):
    """
    Performs spilling given a register map and the set of original virtual registers, with some additional information. At the end, outputs the spilling code as well as the complete register mapping (with every virtual register mapped to a physical register). Uses t0-t2 for spilling (since a single instruction should not have more than three registers).

    Args:
        reg_map: the register mapping given by the allocator
        instr: the MCInstruction to perform spilling on
        offsets: the map from virtual register to the frame pointer offset on the stack
        load: whether this is for loading or storing

    Returns:
        save: a list of MCInstructions which is the spill save code
        restore: a list of MCInstructions which is the spill restore code
        new_args: the physical registers of the instruction
    """
    # NOTE: it's assumed that the position at $fp will be used for saving the register used here
    save = []
    restore = []
    new_args = []

    curr_temp = 0
    # for phys, ir in zip(phys_reg, ir_regs):
    for virtual in instr.regs:
        physical = reg_map[virtual]
        if physical == "spill":
            temp_reg = "$t%d" % curr_temp
            save.append(MCInstruction("sw", regs=[temp_reg, "$fp"], offset=offsets[virtual]))
            restore.append(MCInstruction("lw", regs=[temp_reg, "$fp"], offset=offsets[virtual]))
            new_args.append(temp_reg)
            curr_temp += 1
        else:
            new_args.append(physical)

    return save, restore, new_args

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

#NOTE: this function is not fully implemented
def convert_instr(reg_map, instr: MCInstruction, offsets: Dict[str, int]) -> List[MCInstruction]:
    """
    Convert a single instruction from using virtual register to physical register. Also, if this instruction is `call` or `callr`, then it's also changed to an actual machine instruction.
    Args:
        - reg_map: the register map in this basic block
        - instr: the instruction to be changed
        - offsets: offsets dictionary
    Return:
        - a list of instruction that's equivalent
    """
    # TODO: assume the caller's stack is already even, add padding if the number of args that need to be passed through the stack is odd
    output = []
    # physical_regs = [reg_map[virtual_reg] for virtual_reg in instr.regs]
    curr_temp = 0
    for i in range(len(instr.regs)):
        save, restore, new_regs = spill(reg_map, instr, offsets) # it's fine to call this on non-spilling since the code arrays will be empty
        output += save
        instr.regs = new_regs
        output.append(instr)
        output += restore

    # count the number of arguments

    # NOTE: this if is at this level because the args and dests still need to be translated to physical registers first
    # FIXME: implement the rest of this. Right now only intrinsics is done
    if instr.op == "callr" and instr.op == "call":
        intrinsics = ["geti", "getf", "getc", "puti", "putf", "putc"]
        if instr.name in intrinsics:
            convert_intrinsic(instr)
        output = []
        # ------------ intergrate this ------------------ #
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

        spill_count = list(reg_map.values()).count("spill")
        # ------------ intergrate this ------------------ #

        if spill_count != 0:
            spill_load, spill_map = spill(spill_count, reg_map, instr.regs, offsets, load=True)
            output += spill_load
            # for i in range(len(copy.regs)):
                # if copy.regs[i] == "spill":
                    # copy.regs[i] = spill_map[orig_regs[i]]
            new_regs = [spill_map[r] for r in instr.regs]

            spill_store, _ = spill(spill_count, reg_map, instr.regs, offsets, load=False)

    return output


def load_and_save_locals(reg_map: Dict[str, int], offsets: Dict[str, int]) -> Tuple[List[MCInstruction], List[MCInstruction]]:
    load = []
    save = []
    fp = "$fp"

    for virt, phys in reg_map:
        offset = offsets[virt]
        load.append(MCInstruction("lw", regs=[phys, fp], offset=offset))
        save.append(MCInstruction("sw", regs=[phys, fp], offset=offset))

    return load, save

def translate_body(function: MCFunction, offsets: Dict[str, int]) -> List[MCInstruction]:
    """
    Translates the body of a function one by one. Should call methods like convert_instr.

    Args:
        - function: the MCFunction to be translated
    Returns:
        - the translated output (does not include the prologue and epilogue)
    """
    print(function.bbs)
    assert(function.bbs.keys() == function.reg_maps.keys())

    output = []
    for k in function.bbs.keys():
        bb = function.bbs[k]
        reg_map = function.reg_maps[k]
        load, save = load_and_save_locals(reg_map, offsets)
        output += load
        for instr in bb:
            output += convert_instr(reg_map, instr, offsets)
        output += save

    return output

def parse_function(function: MCFunction) -> List[MCInstruction]:
    """
    Parses an MCFunction to a list of machine instructions. This should be the final product that can be outputted to a file.
    Args:
        - function: an MCFunction object
    Return:
        - a list of mc instructions
    """
    # print(reg_map)
    assert(len(function.reg_maps) == len(function.bbs))

    # prologue = get_prologue(function)
    prologue, epilogue, offsets = calling_convention(function)
    print("offsets: ", offsets)
    #NOTE: if the return value above is None that means it's a simple leaf
    translated_body = translate_body(function, offsets)

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
