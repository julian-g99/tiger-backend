# Simple class. Note that myList is a kwarg that defaults to [] if not specefied
class MyClass:
    def __init__(self, myList=[]):
        self.myList = myList
    
    def add(self, item):
        self.myList.append(item)

# A class that recursively steps through a list of items
class R:
    def __init__(self, items):
        self.items = items
        self.run(0, MyClass())
    
    # recursive method
    def run(self, idx, c):
        if (idx < len(self.items)):
             # The strange behavior.
             # Declaring a new instance of MyClass with no value of myList specefied
             # should result in len(newC.myList) == 0 -> true... but watch
            newC = MyClass()
            if (len(newC.myList) > 0):
                print("BUG! newC was just declared and shouldn't have any items in newC.myList")
                for item in newC.myList:
                    print('\t' + str(item))
            print(newC)
            print(hex(id(newC.myList)))

            # newC.add(self.items[idx]) # Without this line, the strange behavior goes away.
            self.run(idx+1, newC)

def main():
    items = [1,2,3]
    r = R(items)

if __name__ == '__main__':
    main()

"""
> python3 pbug.py

output
======

BUG! newC was just declared and shouldn't have any items in newC.myList
        1
BUG! newC was just declared and shouldn't have any items in newC.myList
        1
        2
"""