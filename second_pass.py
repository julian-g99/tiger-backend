from function import Function
from mc_function import MCFunction
from typing import Dict, List
import re
import copy

from mc_instruction import MCInstruction

def spill_count(reg_map: Dict[str, str]) -> int:
    count = 0
    # FIXME: same as below
    for k, v in reg_map.items():
        if v == "spill":
            count += 1
    return count

def saved_count(reg_map: Dict[str, str]):
    pattern = r'^\$s[01234567]$'
    count = 0
    # FIXME: make this work with all the maps in the map
    for k, v in reg_map.items():
        if re.search(pattern, v):
            count += 1

    return count

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
    total = (fp + arr_length + function.spilled_regs + ra + function.saved_regs) * 4

    return total % 2 == 1
    # if total % 2 == 0:
        # return total, False
    # else:
        # return total + 1, True

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
    if function.stack_type() == "simple_leaf":
        return None
    # prologue of the calling convention
    prologue = []
    offsets = {}
    sp = "$sp"
    fp = "$fp"

    # make space for fp and save
    prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=-4))
    prologue.append(MCInstruction("move", regs=[fp, sp]))

    # make space for array
    curr_offset = -4
    for arr in function.int_arrs:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=arr[1]*4)) # arr[1] should the size
        offsets[arr[0]] = curr_offset
        curr_offset -= arr[1] * 4

    # make space for local variables
    for val in function.int_vals:
        prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=-4))
        offsets[val] = curr_offset
        curr_offset -= 4

    # FIXME: save the s registers

    # if curr_offset + function.saved_regs_count % 2 == 1:
    if needs_pad(function):
        prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=4)) # is this consistent with register alloc

    # prologue.append(MCInstruction("addiu", regs=[sp, sp], offset=function.saved_regs_count*4))
    # curr_offset += function.saved_regs_count

    # for i in range(function.saved_regs_count):
        # prologue.append(MCInstruction("sw", regs=["$sp", "$sp"], offset=i*4))

    return prologue, offsets


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


def convert_instr(reg_map, instr: MCInstruction, offsets: Dict[str, int]) -> List[MCInstruction]:
    output = []

    # orig_regs = instr.regs
    # copy = copy.deepcopy(instr)
    # copy.regs = [reg_map[r] for r in copy.regs]
    # spill_count = copy.regs.count("spill")
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
    for bb in function.bbs:
        for instr in bb:
            print(instr)
            # FIXME: change this to actually translate the function, might want to refactor convert_instr first

def parse_function(function: MCFunction):
    # print(reg_map)
    assert(len(function.reg_maps) == len(function.bbs))

    # prologue = get_prologue(function)
    prologue, epilogue, offsets = calling_convention(function)
    #NOTE: if the return value above is None that means it's a simple leaf
    translated_body = translate_body(function)

def test():
    reg_map = {"x0": "$t0", "x1": "$s10", "x2": "$s7", "x3": "$s3"}
    print(saved_count(reg_map))


if __name__ == "__main__":
    test()

