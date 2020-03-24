class SymbolicMap:
    def __init__(self):
        self.dict = dict()
        self.curr = 0

    def __getitem__(self, key):
        if key not in self.dict.keys():
            self.dict[key] = "x%d" % self.curr
            self.curr += 1
        return self.dict[key]

    def __setitem__(self, key, value):
        if key not in self.dict.keys():
            self.dict[key] = "x%d" % self.curr
            self.curr += 1
        self.dict[key] = value

def test():
    u_map = SymbolicMap()
    print(u_map['xddd'])
    print(u_map['xd'])


if __name__ == "__main__":
    test()
