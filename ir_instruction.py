class IRInstruction:
    def __init__(self, line, instruction_type, argument_list):
        self.line = line
        self.instruction_type = instruction_type
        self.argument_list = argument_list

        def_arr = ['val_assign',
             'sub',
             'add',
             'mult',
             'div',
             'and',
             'or',
             'callr',
             'array_load',
             'array_assign']
        use_arr = ['val_assign',
             'sub',
             'add',
             'mult',
             'div',
             'and',
             'or',
             'breq',
             'brneq',
             'brlt',
             'brgt',
             'brleq',
             'brgeq',
             'return',
             'call',
             'callr',
             'array_store',
             'array_load',
             'array_assign']
        critical_arr = ['breq',
                     'brneq',
                     'brlt',
                     'brgt',
                     'brgeq',
                     'brleq',
                     'goto',
                     'function_start',
                     'function_def',
                     'function_end',
                     'function_int_decl',
                     'function_float_decl',
                     'label',
                     'call',
                     'callr',
                     'array_load',
                     'array_store',
                     'return',
                     'array_assign']
        branch_arr = ['breq',
                   'brneq',
                   'brlt',
                   'brgt',
                   'brgeq',
                   'brleq',
                   'goto']

        self.is_def = self.instruction_type in def_arr
        self.is_use = self.instruction_type in use_arr
        self.is_critical = self.instruction_type in critical_arr
        self.is_branch = self.instruction_type in branch_arr
        self.is_goto = self.instruction_type == "goto"
        self.is_label = self.instruction_type == "label"

        # self.succs = []
        # self.preds = []

    def is_metadata(self):
        metadata = ["function_start", "function_def", "function_end",
                    "function_int_decl", "function_float_decl"]
        return self.instruction_type in metadata

    def does_kill(self, other_def):
        return self.argument_list[0] == other_def.argument_list[0]

    def get_uses(self):
        binary_instructions = ['add', 'sub', 'mult', 'div', 'and', 'or']
        branches = ['breq', 'brneq', 'brlt', 'brgt', 'brgeq', 'brleq']
        if self.instruction_type == "val_assign":
            return self.argument_list[1:2]
        elif self.instruction_type in binary_instructions:
            return self.argument_list[1:3]
        elif self.instruction_type in branches:
            return self.argument_list[1:3]
        elif self.instruction_type == "callr":
            return self.argument_list[2:]
        elif self.instruction_type == "call":
            return self.argument_list[1:]
        elif self.instruction_type == "array_store":
            return self.argument_list[:] #NOTE: the last argument should always be a constant
        elif self.instruction_type == "return":
            return self.argument_list[0:1]
        elif self.instruction_type == "array_load":
            return self.argument_list[1:]
        elif self.instruction_type == "array_assign":
            return self.argument_list[1:]
        else:
            return None
    
    #TODO: check if this actually works in place
    def set_use(self, idx, arg):
        binary_instructions = ['add', 'sub', 'mult', 'div', 'and', 'or']
        branches = ['breq', 'brneq', 'brlt', 'brgt', 'brgeq', 'brleq']
        # print("set use called on index: {}, arg: {}".format(idx, arg))
        if self.instruction_type == "val_assign":
            if idx != 0:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[1] = arg
        elif self.instruction_type in binary_instructions:
            if idx >= 2:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[idx+1] = arg
        elif self.instruction_type in branches:
            if idx >= 2:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[idx+1] = arg
        elif self.instruction_type == "callr":
            self.argument_list[idx+2] = arg
        elif self.instruction_type == "call":
            self.argument_list[idx+1] = arg
        elif self.instruction_type == "array_store":
            if idx >= 3:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[idx] = arg
        elif self.instruction_type == "return":
            if idx >= 1:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[idx] = arg
        elif self.instruction_type == "array_load":
            if idx >= 2:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[idx + 1] = arg
        elif self.instruction_type == "array_assign":
            if idx >= 3:
                print("set use out of bounds. instruction:{}, idx: {}, arg:{}"\
                  .format(self.__str__(), idx, arg))
            else:
                self.argument_list[idx] = arg


    def get_write_target(self):
        has_target = ['val_assign', 'array_assign', 'sub', 'add', 'mult', 'div', 'and', 'or', 'callr', 'array_load']
        if self.instruction_type in has_target:
            return self.argument_list[0].strip()
        else:
            return None

    def get_branch_target(self):
        if self.is_branch:
            return self.argument_list[0]
    
    def get_label(self):
        if self.is_label:
            return self.argument_list[0]

    def is_arithmetic(self):
        arithmetics = ['add', 'sub', 'mult', 'div', 'and', 'or']
        return self.instruction_type in arithmetics

    def is_function_call(self):
        return self.instruction_type == "call" or self.instruction_type == "callr"
    
    def __str__(self):
        return "line number: {}, type: {}, argument_list: {}".format(self.line, self.instruction_type, self.argument_list)
