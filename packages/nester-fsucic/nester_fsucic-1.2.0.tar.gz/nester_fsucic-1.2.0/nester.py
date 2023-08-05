"""A module called nester.py made to print out nested lists. It contains one function designed
for that purpose. Updated version."""


def printList(myList, indent=False, level=0):
    for item in myList:
        if(isinstance(item, list)):
            printList(item, indent, level+1)
        else:
            if (indent):
                for tab_space in range(level):
                    print("\t", end='')
            print(item)
