import re
from ir_instruction import IRInstruction


def parse_instructions(fp):
    function_regex = r'^.+ .+(.*):$'
    instructions = []
    with open(fp, 'r') as file:
        line_num = 0
        for line in file:
            if "#start_function" in line:
                instructions.append(IRInstruction(line_num, "function_start", []))
            elif "#end_function" in line:
                instructions.append(IRInstruction(line_num, "function_end", []))
            elif "int-list:" in line:
                instructions.append(IRInstruction(line_num, "function_int_decl", get_variables(line)))
            elif "float-list:" in line:
                instructions.append(IRInstruction(line_num, "function_float_decl", get_variables(line)))
            elif re.match(function_regex, line) != None:
                instructions.append(IRInstruction(line_num, "function_def", [line]))
            elif ":" in line:
                instructions.append(IRInstruction(line_num, "label", [line[len(line) - len(line.strip()) - 1 : line.find(":")]]))
            elif "assign" in line:
                arg_list = get_arguments(line)
                if len(arg_list) == 2:
                    instructions.append(IRInstruction(line_num, "val_assign", arg_list))
                elif len(arg_list) == 3:
                    instructions.append(IRInstruction(line_num, "array_assign", arg_list))
            elif line.strip() == "" :
                continue
            else:
                # opcode = line[len(line) - len(line.strip()) - 1 : line.find(',')]
                opcode = line[len(line) - len(line.lstrip()): line.find(",")]
                arg_list = get_arguments(line)
                instructions.append(IRInstruction(line_num, opcode, arg_list))
            line_num += 1
    return instructions


def get_functions(instructions):
    functions = []
    line = 0
    while line < len(instructions):
        if instructions[line].instruction_type == 'function_start':
            functions.append([instructions[line]])
            line += 1
            while line < len(instructions) and instructions[line].instruction_type != 'function_end':
                functions[-1].append(instructions[line])
                line += 1
            if (line < len(instructions) and instructions[line].instruction_type == 'function_end'):
                functions[-1].append(instructions[line])
            line += 1
    return functions


def flatten_functions(functions):
    instructions = []
    for func in functions:
        for instr in func:
            instructions.append(instr)
    return instructions


def get_arguments(line):
    return [arg.strip() for arg in line.split(", ")[1:]]


def get_variables(line):
    colon_index = line.find(":")
    if colon_index != -1:
        var_sub = line[colon_index + 2:]
        return [var.strip() for var in var_sub.split(", ")]
    else:
        return []


if __name__ == "__main__":
    instructions = parse_instructions("public_test_cases/quicksort/quicksort.ir")
    for i in instructions:
        print(i)
