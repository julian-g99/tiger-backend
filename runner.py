from parser import parse_instructions
from first_pass import find_functions, instr_to_asm
# from register_alloc import NaiveMIPSAllocator, GreedyMIPSAllocator
from allocator import get_live_ranges, NaiveAllocator, LocalAllocator
from second_pass import parse_function
import argparse
import pprint
from mc_function import MCFunction
import re

from cfg import CFG

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
            mc_instr = instr_to_asm(i, function=func)
            translated += mc_instr

        print_first = False
        if print_first:
            print(func.name + ":")
            for i in translated:
                print("\t%s" % i)

        mc_functions.append(MCFunction(name=func.name, args=func.args, int_arrs=func.int_arrs, instrs=translated))


    if args.allocator == "naive":
        for func in mc_functions:
            allocator = NaiveAllocator(func)
            allocator.map_function()
    elif args.allocator == "local":
        for func in mc_functions:
            allocator = LocalAllocator(func)
            allocator.map_function()

            # print(func.name)
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(func.reg_maps)

    # Continue selecting from here
    should_print = True
    if should_print:
        print(".text")
    for function in mc_functions:
        prologue, translated_body, epilogue, rtn = parse_function(function)
        # prologue, translated_body = parse_function(function)
        if should_print:
            print(function.name + ":")
            for i in prologue:
                print("\t%s" % i)
            print()

            for i in translated_body:
                print("\t%s" % i)
            print()

            for i in epilogue:
                print("\t%s" % i)
            print()

            for i in rtn:
                print("\t%s" % i)


if __name__ == "__main__":
    main()
