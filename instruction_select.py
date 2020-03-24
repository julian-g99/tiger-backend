from ir_instruction import IRInstruction
from parser import parse_instructions
from symbolic_map import SymbolicMap
import re


s_map = SymbolicMap()

def is_constant(arg: str) -> bool:
    pattern = r'^-?\d+.?\d*$'
    return bool(re.compile(pattern).search(arg))

def convert_arithmetic(instr: IRInstruction) -> str:
    """
    Converts an arithmetic instruction to assembly
    """
    assert(instr.is_arithmetic())
    assert(not is_constant(instr.argument_list[0]))

    global s_map

    dest, src0, src1 = instr.argument_list
    output = ""
    if instr.instruction_type == "add" or instr.instruction_type == "sub":
        if not is_constant(src0) and not is_constant(src1):
            # neither is constant
            output = "%s %s, %s, %s" % (instr.instruction_type, s_map[dest], s_map[src0], s_map[src1])
        elif not is_constant(src0) and is_constant(src1):
            # src1 is constant
            output = "%si %s, %s, %s" % (instr.instruction_type, s_map[dest], s_map[src0], src1)
        elif is_constant(src0) and not is_constant(src1):
            # src0 is constant
            output = "%si %s, %s, %s" % (instr.instruction_type, s_map[dest], s_map[src1], src0)
        else:
            # both are constant
            output = "move %s, zero\n" % dest # clearing out dest
            output += "addi %s, %s\n" % (dest, src0)
            output += "addi %s, %s" % (dest, src1)
    if instr.instruction_type == "mult":
        # FIXME: currently assumes the result will be 32 bit
        if not is_constant(src0) and not is_constant(src1):
            # neither is constant
            output = "mult %s, %s\n" % (s_map[src0], s_map[src1])
        elif not is_constant(src0) and is_constant(src1):
            # src1 is constant
            output = "addi %s, zero, %s\n" % (s_map[dest], src1)
            output += "mult %s, %s\n" % (s_map[src0], s_map[dest])
        elif is_constant(src0) and not is_constant(src1):
            # src0 is constant
            output = "addi %s, zero, %s\n" % (s_map[dest], src0)
            output += "mult %s, %s\n" % (s_map[src1], s_map[dest])
        else:
            # both are constant
            output = "addi %s, zero, %s\n" % (s_map[dest], src0)
            output += "addi %s, zero, %s\n" % (s_map["multiply_temporary_register"], src1)
            output += "mult %s, %s" % (s_map[dest], s_map["multiply_temporary_register"])
        output += "mflo %s" % (s_map[dest])
    if instr.instruction_type == "div":
        # FIXME: currently only keeps the integer quotient
        if not is_constant(src0) and not is_constant(src1):
            output = "div %s, %s\n" % (s_map[src0], s_map[src1])
        elif not is_constant(src0) and is_constant(src1):
            output = "addi %s, zero, %s\n" % (s_map[dest], src1)
            output += "div %s, %s" % (s_map[src1], s_map[dest])
        elif is_constant(src0) and not is_constant(src1):
            output = "addi %s, zero, %s\n" % (s_map[dest], src0)
            output += "div %s, %s\n" % (s_map[src1], s_map[dest])
        else:
            output = "addi %s, zero, %s\n" % (s_map[dest], src0)
            output += "addi %s, zero, %s\n" % (s_map["division_temporary_register"], src1)
            output += "div %s, %s" % (s_map[dest], s_map["division_temporary_register"])
        output += "mflo %s" % (s_map[dest])
    if instr.instruction_type in ["and", "or"]:
        i_type = instr.instruction_type
        if not is_constant(src0) and not is_constant(src1):
            output = "%s %s, %s, %s" % (i_type, dest, src0, src1)
        elif not is_constant(src0) and is_constant(src1):
            output = "%si %s, %s, %s" % (i_type, dest, src0, src1)
        elif is_constant(src0) and not is_constant(src1):
            output = "%si %s, %s, %s" % (i_type, dest, src1, src0)
        else:
            output = "addi %s, zero, %s\n" % (s_map[dest], src0)
            output += "%si %s, %s, %s" % (i_type, dest, dest, src1)

    return output


def instr_to_asm(instr: IRInstruction) -> str:
    """
    Converts an IRInstruction object into assembly code string
    Curretnly uses only symbolic registers
    """

    output = ""
    if instr.instruction_type == "add":
        assert(not is_constant(instr.argument_list[0])) # dest can't be constant



if __name__ == "__main__":
    instructions = parse_instructions("./test_cases/bfs/bfs.ir")
    for i in instructions:
        if i.is_arithmetic():
            print("original:\n%s" % i)
            print(convert_arithmetic(i))
            print()
