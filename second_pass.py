from function import Function
from first_pass import is_constant
from mc_function import MCFunction
from typing import Dict, List, Tuple
import re
import copy

import pprint

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
    if function.name != "main":
        total = fp + ra + arr_length + num_vars + 10 + len(function.saved_regs)
    else:
        total = fp + arr_length + num_vars + 10 + len(function.saved_regs)

    return total % 2 == 1

def alloc_array(name: str, size: int, offset: int) -> List[MCInstruction]:
    syscode = 9
    output = []
    fp = "$fp"

    # syscall
    output.append(MCInstruction("li", regs=["$v0"], imm=syscode))
    output.append(MCInstruction("li", regs=["$a0"], imm=size*4))
    output.append(MCInstruction("syscall"))

    # store pointer on the stack
    output.append(MCInstruction("sw", regs=["$v0", fp], offset=offset))

    return output

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
    # if not function.has_data:
        # return None

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

    curr_offset = -4
    # make space for arg registers
    for i in range(4):
        arg_reg = "$a%d" % i
        # prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        offsets[arg_reg] = curr_offset
        curr_offset -= 4

    # make space for arrays
    arr_names = []
    for arr in function.int_arrs:
        arr_names.append(arr[0])
        prologue += alloc_array(arr[0], arr[1], curr_offset)
        offsets[arr[0]] = curr_offset
        curr_offset -= 4

    # make space for local variables
    # for greedy local alloc, need to save everything (even non-spilled)
    for val in function.int_vals:
        if val not in arr_names:
            # prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
            offsets[val] = curr_offset
            curr_offset -= 4

    # save all the t registers (as specified in the pdf)
    for i in range(10):
        t_reg = "$t%d" % i
        # if function.name != "main":
        # prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        # prologue.append(MCInstruction("sw", regs=[t_reg, sp], imm=0))
        prologue.append(MCInstruction("sw", regs=[t_reg, fp], offset=curr_offset))
        offsets[t_reg] = curr_offset
        curr_offset -= 4
        # else:
            # prologue.append(MCInstruction("li", regs=[t_reg], imm=0))

    # padding
    if needs_pad(function):
        # prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        curr_offset -= 4

    if function.name != "main":
        # return address
        # prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        prologue.append(MCInstruction("sw", regs=["$ra", fp], offset=curr_offset))
        offsets["$ra"] = curr_offset
        curr_offset -= 4

    # s registers
    for s in function.saved_regs:
        # prologue.append(MCInstruction("addiu", regs=[sp, sp], imm=-4))
        prologue.append(MCInstruction("sw", regs=[s, fp], offset=curr_offset))
        offsets[s] = curr_offset
        curr_offset -= 4

    # now, finally move the sp
    prologue.append(MCInstruction("addiu", regs=[sp, fp], imm=curr_offset+4))

    # epilogue
    epilogue = []

    # restore the s registers
    # for s in function.saved_regs[::-1]:
    for s in function.saved_regs:
        epilogue.append(MCInstruction("lw", regs=[s, fp], offset=offsets[s]))

    if function.name != "main":
        # restore the return address
        epilogue.append(MCInstruction("lw", regs=["$ra", fp], offset=offsets["$ra"]))
        # epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    # restore t registers
    for i in range(10):
        t_reg = "$t%d" % i
        epilogue.append(MCInstruction("lw", regs=[t_reg, fp], offset=offsets[t_reg]))

    # restore the fp
    epilogue.append(MCInstruction("move", regs=[sp, fp])) # moving sp back to fp
    epilogue.append(MCInstruction("lw", regs=[fp, sp], offset=0))
    epilogue.append(MCInstruction("addiu", regs=[sp, sp], imm=4))

    return prologue, epilogue, offsets

# def instr_uses(instr: MCInstruction) -> List[str]:
    # if instr.regs is None or instr.regs == []:
        # return []
    # # only assign for now
    # triples = ["add", "addi", "addu", "addiu",
               # "sub", "subu",
               # "div", "mul",
               # "and", "andi",
               # "or", "ori",
               # "sll"]

    # doubles = ["move", "li"]

    # mems = ["sw", "lw"]

    # branches = ["beq", "bne", "blt", "bgt", "bge", "ble", "blez"]

    # jumps = ["j", "jr"]


    # if instr.op in triples:
        # return instr.regs[1:]
    # elif instr.op in doubles:
        # return instr.regs[1:]
    # elif instr.op in mems:
        # return instr.regs
    # elif instr.op in branches:
        # return instr.regs
    # elif instr.op in jumps:
        # return instr.regs
    # else:
        # raise ValueError("unexpected instruction for instr_uses()")


def spill(reg_map: Dict[str, str], instr: MCInstruction, offsets: Dict[str, int], optimize=False) -> (List[MCInstruction], List[MCInstruction], Dict[str, str]):
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
    save_temp = []
    load_virt = []
    save_virt = []
    load_temp = []
    new_args = []

    curr_temp = 9
    # for phys, ir in zip(phys_reg, ir_regs):
    new_map = {}

    # compute used temp regs in the instruction
    used_temps = set() 
    for virt in instr.regs:
        if virt[0] == "$":
            used_temps.add(virt)
        else:
            phys = reg_map[virt]
            if phys != "spill":
                used_temps.add(phys)


    is_spilled = False
    for virtual in instr.regs:
        if virtual not in new_map:
            if virtual[0] == "$":
                new_args.append(virtual)
                new_map[virtual] = virtual
            else:
                physical = reg_map[virtual]
                if physical == "spill":
                    is_spilled = True
                    temp_reg = "$t%d" % curr_temp

                    while temp_reg in used_temps:
                        curr_temp -= 1
                        assert(curr_temp < 10)
                        temp_reg = "$t%d" % curr_temp
                    # used_temps.add(temp_reg)

                    if optimize:
                        temp_needs_save = temp_reg in reg_map.values()
                        virt_needs_load = virtual in instr.get_uses()
                    else:
                        temp_needs_save = True
                        virt_needs_load = True

                    if temp_needs_save:
                        save_temp.append(MCInstruction("sw", regs=[temp_reg, "$fp"], offset=offsets[temp_reg]))

                    if virt_needs_load:
                        load_virt.append(MCInstruction("lw", regs=[temp_reg, "$fp"], offset=offsets[virtual]))

                    save_virt.append(MCInstruction("sw", regs=[temp_reg, "$fp"], offset=offsets[virtual]))

                    if temp_needs_save:
                        load_temp.append(MCInstruction("lw", regs=[temp_reg, "$fp"], offset=offsets[temp_reg]))

                    new_args.append(temp_reg)
                    new_map[virtual] = temp_reg
                    curr_temp -= 1
                else:
                    new_args.append(physical)
                    new_map[virtual] = physical
        else:
            new_args.append(new_map[virtual])

    prologue = save_temp + load_virt
    epilogue = save_virt + load_temp

    # if is_spilled:
        # print("used temps: ", used_temps)
        # print(reg_map)
        # print(offsets)
        # print("prologue:")
        # for i in prologue:
            # print(i)
        
        # print("instr: ")

        # new_instr = instr
        # new_instr.regs = new_args
        # print(new_instr)

        # print("epilogue:")
        # for i in epilogue:
            # print(i)
        # print()
        # print()
        # print()

    return prologue, epilogue, new_args

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

def convert_instr(reg_map, instr: MCInstruction, offsets: Dict[str, int], epilogue, rtn, optimize=False) -> List[MCInstruction]:
    """
    Convert a single instruction from using virtual register to physical register. Also, if this instruction is `call` or `callr`, then it's also changed to an actual machine instruction.
    Args:
        - reg_map: the register map in this basic block
        - instr: the instruction to be changed
        - offsets: offsets dictionary
    Return:
        - a list of instruction that's equivalent
    """

    if instr.op == "ret":
        return epilogue + rtn

    fp = "$fp"
    if instr.op == "save_arg":
        reg = instr.regs[0]
        return [MCInstruction("sw", regs=[reg, fp], offset=offsets[reg])]
    if instr.op == "restore_arg":
        reg = instr.regs[0]
        return [MCInstruction("lw", regs=[reg, fp], offset=offsets[reg])]

    # TODO: assume the caller's stack is already even, add padding if the number of args that need to be passed through the stack is odd
    output = []
    # physical_regs = [reg_map[virtual_reg] for virtual_reg in instr.regs]
    curr_temp = 0
    if instr.regs is None:
        return [instr]
    prologue = []
    epilogue = []
    save, restore, new_regs = spill(reg_map, instr, offsets, optimize=optimize) # it's fine to call this on non-spilling since the code arrays will be empty

    output += prologue
    output += save
    instr.regs = new_regs
    output.append(instr)
    output += restore
    output += epilogue

    return output

def load_and_save_locals(reg_map: Dict[str, int], offsets: Dict[str, int]) -> Tuple[List[MCInstruction], List[MCInstruction]]:
    load = []
    save = []
    fp = "$fp"

    # pprint.pprint(reg_map)

    # print(offsets)

    arg_pattern = re.compile(r"\$a[0123]")

    for virt, phys in reg_map.items():
        if phys != "spill" and arg_pattern.match(phys) is None:
            offset = offsets[virt]
            load.append(MCInstruction("lw", regs=[phys, fp], offset=offset))
            save.append(MCInstruction("sw", regs=[phys, fp], offset=offset))

    return load, save

def translate_body(function: MCFunction, offsets: Dict[str, int], epilogue, rtn, optimize=False) -> Tuple[bool, List[MCInstruction]]:
    """
    Translates the body of a function one by one. Should call methods like convert_instr.

    Args:
        - function: the MCFunction to be translated
    Returns:
        - the translated output (does not include the prologue and epilogue)
    """
    assert(function.bbs.keys() == function.reg_maps.keys())

    output = []
    sorted_keys = list(function.bbs.keys())
    sorted_keys.sort()
    has_returned = False
    for k in sorted_keys:
        bb = function.bbs[k]
        reg_map = function.reg_maps[k]

        load, save = load_and_save_locals(reg_map, offsets)
        if bb[0].op == "label":
            label = bb.pop(0)
            output.append(label)
        # if len(bb) > 0 and (bb[-1].is_branch() or bb[-1].is_jump()):
            # jump = bb.pop(-1)
            # jump = convert_instr(reg_map, jump, offsets, epilogue, rtn)
            # output += save
            # output += jump

        output += load
        for instr in bb:
            if instr.op == "ret":
                has_returned = True
            
            if instr.is_jump() or instr.is_branch():
                output += save
            output += convert_instr(reg_map, instr, offsets, epilogue, rtn, optimize=optimize)
        output += save

        # if jump is not None:
            # output += jump

    return has_returned, output

def return_function(function: MCFunction) -> [List[MCInstruction]]:
    output = []
    syscode = 10
    if function.name == "main":
        output.append(MCInstruction("li", regs=["$v0"], imm=syscode))
        output.append(MCInstruction("syscall"))
    else:
        output.append(MCInstruction("jr", regs=["$ra"]))
    return output

def parse_function(function: MCFunction, optimize=False) -> Tuple[List[MCInstruction], List[MCInstruction], List[MCInstruction], List[MCInstruction]]:
    """
    Parses an MCFunction to a list of machine instructions. This should be the final product that can be outputted to a file.
    Args:
        - function: an MCFunction object
    Return:
        - a list of mc instructions
    """
    assert(len(function.reg_maps) == len(function.bbs))

    for _, reg_map in function.reg_maps.items():
        for i, arg in enumerate(function.args):
            if i < 4:
                reg_map[arg] = "$a%d" % i
            else:
                reg_map[arg] = "spill"

    # prologue = get_prologue(function)
    prologue, epilogue, offsets = calling_convention(function)

    # if function.name == "main":
        # print(function.name)
        # # pp = pprint.PrettyPrinter(indent=2)
        # pprint.pprint(offsets)

    curr_offset = 4
    for arg in function.args[4:]:
        offsets[arg] = curr_offset 
        curr_offset += 4

    # sorted_offsets = [(k, v) for k, v in sorted(offsets.items(), key=lambda item: item[1])]
    #NOTE: if the return value above is None that means it's a simple leaf
    rtn = return_function(function)

    has_returned, translated_body = translate_body(function, offsets, epilogue, rtn, optimize=optimize)

    # rtn += epilogue


    # return prologue, translated_body, epilogue, rtn
    if has_returned:
        return prologue, translated_body, [], []
    else:
        return prologue, translated_body, epilogue, rtn
    # return prologue, translated_body

def test():
    i = 0 # using this as nop


if __name__ == "__main__":
    test()
