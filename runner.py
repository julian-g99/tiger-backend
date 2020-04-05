from parser import parse_instructions
from instruction_select import find_functions, instr_to_asm


def main():
    instructions = parse_instructions("./test_cases/bfs/bfs.ir")
    functions = find_functions(instructions)
    output = []
    for f in functions:
        translated = []
        for i in f.body():
            translated += instr_to_asm(i)
            if instr_to_asm(i) == ['not implemented']:
                print(i)
        output.append(translated)


if __name__ == "__main__":
    main()
