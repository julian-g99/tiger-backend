from typing import List, Tuple
import functools
from mc_instruction import MCInstruction
from mc_function import MCFunction
from cfg import CFG
import re
from pprint import PrettyPrinter

def convert_map(temp_map):
    reg_map = {}
    for phys, virts in temp_map.items():
        for virt in virts:
            reg_map[virt] = phys

    return reg_map

def should_map(reg: str, args: List[str]):
    pattern = re.compile(r"\$[stav]\d|zero|$\d+")

    not_physical = pattern.match(reg) is None
    not_arg = reg not in args

    return not_physical and not_arg

def reg_instr_counts(reg, instrs):
    count = 0
    for instr in instrs:
        if instr.regs is not None and reg in instr.regs:
            count += 1

    return count

def compare_regs(reg1, reg2, instrs: List[MCInstruction]):
    count1 = reg_instr_counts(reg1, instrs)
    count2 = reg_instr_counts(reg2, instrs)

    count_diff = count1 - count2
    if count_diff != 0:
        return count_diff
    else:
        if reg1 < reg2:
            return -1
        else:
            return 1

def sorted_regs(regs: List[str], instrs: List[MCInstruction]):
    sorted_regs = sorted(regs, key=lambda reg: reg_instr_counts(reg, instrs), reverse=True)
    return sorted_regs

def next_def(reg, d, i):
    if reg not in d:
        return None

    elements = d[reg]
    elements = list(elements)
    elements.sort()
    for ele in elements:
        if ele >= i:
            return ele

    return None

def next_use(reg, d, i, total_length):
    if reg not in d:
        return None

    elements = d[reg]
    elements =list(elements)
    elements.sort()

    for ele in elements:
        if ele >= i:
            return ele

    return None

def does_interfere(range1: Tuple[int, int], range2: Tuple[int, int]):
    if range1 is None or range2 is None:
        return False

    start1, end1 = range1
    start2, end2 = range2

    return start1 <= end2 and start2 <= end1

def get_regs_from_instructions(instrs: List[MCInstruction], args):
    regs = []
    for instr in instrs:
        if instr.regs is not None:
            instr_regs = [reg for reg in instr.regs if should_map(reg, args)]
            regs += instr_regs

    return set(regs)

def get_live_ranges(instrs: List[MCInstruction], args):
    # NOTE: here the index is right before the instruction (program point)
    regs = get_regs_from_instructions(instrs, args)

    uses = {}
    defs = {}

    for i, instr in enumerate(instrs):
        if instr.regs is not None:
            for reg in instr.get_uses():
                if should_map(reg, args):
                    if reg not in uses:
                        uses[reg] = set()
                    uses[reg].add(i)
            for reg in instr.get_defs():
                if should_map(reg, args):
                    if reg not in defs:
                        defs[reg] = set()
                    defs[reg].add(i)

    use_keys = set(uses.keys())
    def_keys = set(defs.keys())
    assert(use_keys.union(def_keys) == regs)
    # print(use_keys.union(def_keys))
    # assert()

    live_points = {reg: set() for reg in regs}

    for reg in regs:
        for i in range(len(instrs)+1):
            n_use = next_use(reg, uses, i, len(instrs))
            n_def = next_def(reg, defs, i)

            if n_def is None:
                live_points[reg].add(i)
            elif n_use is not None:
                if i <= n_use and n_use <= n_def:
                    live_points[reg].add(i)


    live_ranges = {}
    for reg in regs:
        live_set = live_points[reg]
        if len(live_set) == 0:
            live_ranges[reg] = None
        else:
            live_ranges[reg] = min(live_set), max(live_set)


    return live_ranges

class NaiveAllocator:
    def __init__(self, function: MCFunction):
        # self.regs = get_regs_from_instructions(instructions)
        # self.bbs = get_bbs_from_instructions(instructions)
        self.function = function
        self.cfg = CFG(function.body)
        self.reg_maps = self.get_reg_maps()

    def get_reg_maps(self):
        reg_maps = {}

        for bbid, instrs in self.cfg.bbs.items():
            regs = get_regs_from_instructions(instrs, self.function.args)
            reg_map = {reg: "spill" for reg in regs}
            reg_maps[bbid] = reg_map

        return reg_maps

    def map_function(self):
        self.function.set_bbs(self.cfg.bbs)
        self.function.set_reg_maps(self.reg_maps)

class LocalAllocator:
    def __init__(self, function: MCFunction, use_saved=False):
        self.cfg = CFG(function.body)
        self.use_saved = use_saved
        self.function = function
        self.reg_maps = self.get_reg_maps()

    def get_reg_maps(self):
        reg_maps = {}

        for bbid, instrs in self.cfg.bbs.items():
            reg_map = LocalAllocator.alloc_for_bb(instrs, use_saved=self.use_saved, args=self.function.args)
            reg_maps[bbid] = reg_map

        return reg_maps

    def map_function(self):
        self.function.set_bbs(self.cfg.bbs)
        self.function.set_reg_maps(self.reg_maps)

    @staticmethod
    def alloc_for_bb(instrs: List[MCInstruction], use_saved=False, args=None):
        regs = get_regs_from_instructions(instrs, args)
        live_ranges = get_live_ranges(instrs, args)
        adj_list = {reg: set() for reg in regs}
        for i, reg1 in enumerate(regs):
            for j, reg2 in enumerate(regs):
                if i != j:
                    reg1_range = live_ranges[reg1]
                    reg2_range = live_ranges[reg2]
                    if does_interfere(reg1_range, reg2_range):
                        adj_list[reg1].add(reg2)
                        adj_list[reg2].add(reg1)

        phys_regs = ["$t%d" % i for i in range(10)]
        if use_saved:
            phys_regs += ["$s%d" % i for i in range(8)]

        ordered_regs = sorted_regs(regs, instrs)

        temp_map = {phys: set() for phys in phys_regs}
        temp_map["spill"] = set()


        while len(ordered_regs) != 0:
            reg = ordered_regs.pop(0)
            mapped = False
            for phys in phys_regs:
                curr = temp_map[phys]
                if adj_list[reg].isdisjoint(curr):
                    temp_map[phys].add(reg)
                    mapped = True
                    break
            if not mapped:
                temp_map["spill"].add(reg)

        reg_map = convert_map(temp_map)

        return reg_map
