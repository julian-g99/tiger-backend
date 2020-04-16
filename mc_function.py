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
        self.calls_others = calls_others(bbs)
        if self.reg_maps is not None:
            self.stack_type = self.get_stack_type()

    def set_reg_maps(self, reg_maps):
        self.reg_maps = reg_maps
        self.saved_regs = get_saved_regs(self.reg_maps)
        self.spill_regs = get_spill_regs(self.reg_maps)
        if self.bbs is not None:
            self.stack_type = self.get_stack_type()

    def get_stack_type(self):
        assert(self.saved_regs is not None)
        assert(self.spill_regs is not None)
        assert(self.calls_others is not None)

        if self.calls_others:
            return "nonleaf"
        elif len(self.saved_regs) != 0 or len(self.spill_regs) != 0:
            return "data leaf"
        else:
            return "simple leaf"

    @staticmethod
    def get_saved_regs(reg_maps):
        saved_regs = set()
        saved_pattern = re.compile("\$s\d+")
        for reg_map in reg_maps:
            for _, mp in reg_map.items():
                for _, reg in mp.items():
                    if saved_pattern.match(reg):
                        saved_regs.add(reg)
        return saved_regs

    @staticmethod
    def get_spill_regs(reg_maps):
        spill_regs = set()
        for reg_map in reg_maps:
            for _, mp in reg_map.items():
                for ir, mc in mp.items():
                    if mc == "spill":
                        spill_regs.add(ir)
        return spill_regs

    @staticmethod
    def calls_others(bbs):
        for bb in bbs:
            for instr in bb:
                if instr.op == "ja":
                    return True

        return False
