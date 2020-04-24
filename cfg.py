from mc_instruction import MCInstruction
from typing import List

class CFG:
    def __init__(self, instructions: List[MCInstruction]):
        self.instructions = instructions
        self.bbs = self.get_blocks()

    def get_blocks(self) -> List[List[MCInstruction]]:
        leaders = CFG.get_leaders(self.instructions)

        blocks = {}
        bbid = 0

        for i in range(len(leaders)):
            start = leaders[i]
            if i == len(leaders) - 1:
                end = len(self.instructions)
            else:
                end = leaders[i+1]

            # blocks.append(self.instructions[start:end])
            blocks[bbid] = self.instructions[start:end]
            bbid += 1

        # all instructions are in exactly one block
        alls = []
        for i, block1 in blocks.items():
            alls += block1
            for j, block2 in blocks.items():
                if i != j:
                    set1 = set(block1)
                    set2 = set(block2)
                    # if not set1.isdisjoint(set2):
                        # for i in set1:
                            # print(i)
                        # print()
                        # for i in set2:
                            # print(i)
                        # assert()
                    assert(set1.isdisjoint(set2))

        assert(len(alls) == len(self.instructions))

        return blocks



    @staticmethod
    def get_leaders(instructions: List[int]):
        leaders = set()
        targets = set()
        num = len(instructions)

        leaders.add(0) # first instruction

        # add all the nexts and add the targets
        for i, instr in enumerate(instructions):
            if instr.is_branch():
                next_instr = i + 1
                if next_instr < num:
                    leaders.add(next_instr)

                targets.add(instr.target)
            if instr.is_jump():
                targets.add(instr.target)

        for i, instr in enumerate(instructions):
            if instr.op == "label" and instr.target in targets:
                leaders.add(i)

        leaders = list(leaders)
        leaders.sort()
        return leaders
