from parser import parse_instructions
from first_pass import find_functions, instr_to_asm
from register_alloc import NaiveMIPSAllocator, GreedyMIPSAllocator
from second_pass import parse_function
import argparse
import pprint
from mc_function import MCFunction
import re

parser = argparse.ArgumentParser()
parser.add_argument('--allocator', type=str, default='greedy', help='the type of register allocation to perform (\'naive\' or \'greedy\')')
parser.add_argument('--input', type=str, help='input file')
parser.add_argument('--output', type=str, default='out.s', help='output file')


def main():
    args = parser.parse_args()
    fname = args.input
    allocator = None
    instructions = parse_instructions(fname)
    functions = find_functions(instructions)
    mc_functions = []
    for func in functions:
        translated = []
        for i in func.body():
            mc_instr = instr_to_asm(i)
            translated += mc_instr
        mc_functions.append(MCFunction(name=func.name, int_arrs=func.int_arrs, instrs=translated))

    if args.allocator == 'greedy':
        allocator = GreedyMIPSAllocator([])
    else:
        allocator = NaiveMIPSAllocator([])

    for function in mc_functions:
        pattern = re.compile(r"(?!\$)")
        allocator.mapMCFunction(function, target=pattern, physical='$t', regex=True)

    # Continue selecting from here
    for function in mc_functions:
        print(function.name + ":")
        res = parse_function(function)
        for i in res:
            print("\t%s" % i)


if __name__ == "__main__":
    main()
