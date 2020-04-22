import argparse

from MIPSProgram import MIPSProgram

parser = argparse.ArgumentParser()
parser.add_argument('--allocator', type=str, default='greedy', help='the type of register allocation to perform (\'naive\' or \'greedy\')')
parser.add_argument('--input', type=str, help='input file')
parser.add_argument('--output', type=str, default='out.s', help='output file')


def main():
    args = parser.parse_args()
    fname = args.input
    program = MIPSProgram(inputTigerIRFile=fname)
    for f in program.functions:
        print("====")
        for i in f.instructions:
            print(i)

if __name__ == "__main__":
    main()
    # python3 runner.py --input './examples/exampleir.txt'
