import re
from ir_instruction import IRInstruction
from typing import List

class Function:
    def __init__(self, instructions: List[IRInstruction]):
        self.instructions = instructions
        self.__check_types()
        self.return_type, self.name = self.__get_rtype_and_name()
        self.args = self.__get_args()
        self.int_vals, self.int_arrs = self.__get_int_locals()

        num_temps = 10
        self.saved_regs_count = len(self.int_vals) + len(self.int_arrs) - num_temps
        self.has_array = len(self.int_arrs) == 0
        self.has_data = saved_regs_count != 0 or self.has_array

        if self.__is_leaf() and not self.has_data:
            self.stack_type = "simple_leaf"
        elif self.__is_leaf():
            self.stack_type = "data_leaf"
        else:
            self.stack_type = "nonleaf"


    def __check_types(self):
        instructions = self.instructions
        assert(instructions[0].instruction_type == "function_start")
        assert(instructions[1].instruction_type == "function_def")
        assert(instructions[2].instruction_type == "function_int_decl")
        assert(instructions[3].instruction_type == "function_float_decl")
        assert(instructions[-1].instruction_type == "function_end")

    def __get_args(self):
        s = self.instructions[1].argument_list[0]
        opening = s.index("(")
        closing = s.index(")")
        arg_list = s[opening+1: closing]

        return arg_list.split(", ")


    def __get_rtype_and_name(self):
        s = self.instructions[1].argument_list[0]
        words = s[:s.index("(")].split()
        return words[0], words[1]

    def __get_int_locals(self):
        pattern = r'\[\d*\]'
        regex = re.compile(pattern)

        decl = self.instructions[2]
        vals = []
        arrays = []

        for arg in decl.argument_list:
            if regex.search(arg):
                opening = arg.index("[")
                closing = arg.index("]")
                arrays.append((arg[: opening], arg[opening+1: closing]))
            else:
                vals.append(arg)

        return vals, arrays

    def __is_leaf(self):
        for i in self.instructions:
            if i.instruction_type == "call" or i.instruction_type == "callr":
                return True

        return False

    def body(self):
        return self.instructions[4:-1]
