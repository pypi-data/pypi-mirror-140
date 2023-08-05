"""A module called nester.py made to print out nested lists. It contains one function designed
for that purpose. Updated version."""


def printList(myList, level):
    for item in myList:
        if(isinstance(item, list)):
            printList(item, level+1)
        else:
            for tab_space in range(level):
                print("\t", end='')
            print(item)
