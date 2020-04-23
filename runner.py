import argparse
import re

from mips_program import MIPSProgram
import register_allocator as ra
from control_flow_graph import CFG

parser = argparse.ArgumentParser()
parser.add_argument('--allocator', type=str, default='greedy', help='the type of register allocation to perform (\'naive\' or \'greedy\')')
parser.add_argument('--input', type=str, help='input file')
parser.add_argument('--output', type=str, default='out.s', help='output file')


def main():
    args = parser.parse_args()
    inputFname = args.input
    program = MIPSProgram(inputTigerIRFile=inputFname)
    #cfg = CFG(function.instructions)
    # for bb in cfg.bbs:
    #     print("==== {} ====".format(bb.pp))
    #     for instruction in bb:
    #         print(instruction)
    #instructions = cfg.getInstructionsFromBBs()

    outputFname = args.output
    program._writeToSFile(outputFname)

if __name__ == "__main__":
    main()
    # python3 runner.py --input './examples/exampleir.txt'
