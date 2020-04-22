from typing import List
from mc_instruction import MCInstruction
import re

class MCFunction:
    def __init__(self, name: str, args: List[str], int_arrs: List[str], instrs: List[MCInstruction]):
        self.int_arrs = int_arrs
        self.name = name
        self.args = args
        self.body = instrs
        self.bbs = None
        self.reg_maps = None


    def num_vars(self):
        assert(self.reg_maps is not None)
        total = 0
        virtuals = set()
        for bbid, reg_map in self.reg_maps.items():
            for virtual, physical in reg_map.items():
                virtuals.add(virtual)
        return len(virtuals)


    def set_bbs(self, bbs):
        self.bbs = bbs
        self.calls_others = MCFunction.calls_others(bbs)
        if self.reg_maps is not None:
            self.has_data = self.has_data()

    def set_reg_maps(self, reg_maps):
        self.reg_maps = reg_maps
        self.saved_regs = MCFunction.get_saved_regs(self.reg_maps)
        self.spill_regs = MCFunction.get_spill_regs(self.reg_maps)
        self.num_vars = self.num_vars()
        self.int_vals = MCFunction.get_int_vals(reg_maps)
        if self.bbs is not None:
            self.has_data = self.has_data()

    def has_data(self):
        assert(self.saved_regs is not None)
        assert(self.spill_regs is not None)
        assert(self.calls_others is not None)

        return len(self.saved_regs) != 0 or len(self.spill_regs) != 0
        # if self.calls_others:
            # return "nonleaf"
        # elif len(self.saved_regs) != 0 or len(self.spill_regs) != 0:
            # return "data leaf"
        # else:
            # return "simple leaf"

    @staticmethod
    def get_saved_regs(reg_maps):
        saved_regs = set()
        saved_pattern = re.compile("\$s\d+")
        for _, reg_map in reg_maps.items():
            for _, reg in reg_map.items():
                if saved_pattern.match(reg):
                    saved_regs.add(reg)
        output = list(saved_regs)
        output.sort()
        return output

    @staticmethod
    def get_spill_regs(reg_maps):
        spill_regs = set()
        for _, reg_map in reg_maps.items():
            for ir, reg in reg_map.items():
                if reg == "spill":
                    spill_regs.add(ir)
        return spill_regs

    @staticmethod
    def calls_others(bbs):
        for bbid, bb in bbs.items():
            for instr in bb:
                if instr.op == "jal":
                    return True

        return False

    @staticmethod
    def get_int_vals(reg_maps):
        int_vals = set()
        for _, reg_map in reg_maps.items():
            for virt, phys in reg_map.items():
                int_vals.add(virt)

        int_vals = list(int_vals)
        int_vals.sort()
        return int_vals
