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
            mc_instr = instr_to_asm(i, function=func)
            translated += mc_instr
        print(func.name + ":")
        for i in translated:
            print("\t%s" % i)
        mc_functions.append(MCFunction(name=func.name, args=func.args, int_arrs=func.int_arrs, instrs=translated))

    if args.allocator == 'greedy':
        allocator = GreedyMIPSAllocator([])
    else:
        allocator = NaiveMIPSAllocator([])

    for function in mc_functions:
        pattern = re.compile(r"\$[stav]\d|zero|\d+")
        allocator.mapMCFunction(function, target=pattern, physical='$t', regex=True)

    should_print = False
    # Continue selecting from here
    if should_print:
        print(".text")
    for function in mc_functions:
        prologue, translated_body, epilogue, rtn = parse_function(function)
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
