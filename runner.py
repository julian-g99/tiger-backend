import argparse

from mips_program import MIPSProgram

parser = argparse.ArgumentParser()
parser.add_argument('--allocator', type=str, default='greedy', help='the type of register allocation to perform (\'naive\' or \'greedy\')')
parser.add_argument('--input', type=str, help='input file')
parser.add_argument('--output', type=str, default='out.s', help='output file')


def main():
    args = parser.parse_args()
    inputFname = args.input
    program = MIPSProgram(inputTigerIRFile=inputFname)
    outputFname = args.output
    program._writeToSFile(outputFname)

if __name__ == "__main__":
    main()
    # python3 runner.py --input './examples/exampleir.txt'
