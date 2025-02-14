from parser import parse_instructions
from instruction_select import find_functions, instr_to_asm
from register_alloc import NaiveMIPSAllocator, GreedyMIPSAllocator
from second_pass import parse_function
import argparse
import pprint

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
    # for i in functions[0].body():
        # print(i)
    translated_functions = []
    for func in functions:
        translated = []
        for i in func.body():
            translated += instr_to_asm(i)
        # Demo code for outputtiong instructions
        # if args.allocator == 'naive':
        #     allocator = NaiveMIPSAllocator(translated)
        #     alloc_translated = allocator.allocProgram(target='x')
        #     translated_functions.append(alloc_translated)
        # else:
        #     allocator = GreedyMIPSAllocator(translated)
        #     alloc_translated = allocator.allocProgram(target='x')
        #     translated_functions.append(alloc_translated)
        # fname = args.output
        # with open(fname, 'w') as fp:
        #     for func in translated_functions:
        #         block_start_lines = []
        #         for block in func:
        #             start_line = block.pp
        #             block_start_lines.append(block.pp)
        #         block_start_lines.sort()
        #         instructions = []
        #         for start_line in block_start_lines:
        #             for block in func:
        #                 if block.pp == start_line:
        #                     for instruction in block:
        #                         fp.write('\n' + str(instruction))

        # Demo code for just getting register maps
        maps = {} # The key is the line number of the leader of the basic block the register map is for. The value is the reg map
        for t in translated:
            print(t)
        if args.allocator == 'naive':
            allocator = NaiveMIPSAllocator(translated)
            regMap = allocator.getRegMap(target='x', physical='$t')
            maps[0] = regMap   
        else:
            allocator = GreedyMIPSAllocator(translated)
            regMaps = allocator.getRegMaps(target='x', physical='$t')
            maps = regMaps
        pp = pprint.PrettyPrinter(indent=1)
        pp.pprint(maps)

        output = parse_function(func, maps[0])

    # Continue selecting from here

    # Demo code for just getting the register maps



if __name__ == "__main__":
    main()
