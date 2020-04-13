from typing import List
from mc_instruction import MCInstruction

class MCFunction:
    def __init__(self, int_vals: List[str], int_arrs: List[str], instrs: List[MCInstruction]):
        self.int_vals = int_vals
        self.int_arrs = int_arrs

        self.body = instrs


    def set_bbs(self, bbs):
        self.bbs = bbs

    def set_reg_maps(self, reg_maps):
        self.reg_maps = reg_maps
