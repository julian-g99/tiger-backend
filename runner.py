from parser import parse_instructions
from first_pass import find_functions, instr_to_asm
from register_alloc import NaiveMIPSAllocator, GreedyMIPSAllocator
from second_pass import parse_function
import argparse
import pprint
from mc_function import MCFunction

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
        for i in translated:
            print(i)
        mc_functions.append(MCFunction(int_vals=func.int_vals, int_arrs=func.int_arrs, instrs=translated))
    
    # if args.allocator == 'greedy':
        # allocator = GreedyMIPSAllocator([])
    # else:
        # allocator = NaiveMIPSAllocator([])

    # for function in mc_functions:
        # allocator.mapMCFunction(function, target='x', physical='$t')
        # # print("regMaps: {}".format(function.reg_maps))
        # # print("bbs: {}".format(function.bbs))

    # # Continue selecting from here
    # for function in mc_functions:
        # # print(function.reg_maps)
        # res = parse_function(function)

    # # Demo code for just getting the register maps



if __name__ == "__main__":
    main()
