from typing import List
from mc_instruction import MCInstruction
import re

class MCFunction:
    def __init__(self, int_vals: List[str], int_arrs: List[str], instrs: List[MCInstruction]):
        self.int_vals = int_vals
        self.int_arrs = int_arrs

        self.body = instrs


    def set_bbs(self, bbs):
        self.bbs = bbs

    def set_reg_maps(self, reg_maps):
        self.reg_maps = reg_maps

    def get_saved_count(self):
        assert(self.reg_maps is not None)

    def calls_others(self):
        for instr in self.body:
            if instr.op == "ja": # TODO: check if this op is correct
                return True
        return False

    def has_data(self):
        assert(self.reg_maps is not None)
        assert(self.bbs is not None)

        s_regs_pattern = re.compile("\$s\d")
        spill_count = 0
        seen_saved = set()
        for reg_map in self.reg_maps:
            for bbid, rm in reg_map.items():
                for ir_name, mc_name in rm.items():
                    if s_regs_pattern.match(mc_name):
                        seen_saved.add(mc_name)
                    elif mc_name == "spill":
                        spill_count += 1

        if spill_count == 0 and len(seen_saved) == 0:
            return False
        else:
            return True
