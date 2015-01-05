import argparse
import xml.etree.ElementTree as ET
from operator import attrgetter

# fuzzy compare XML tree from XML strings
def isFuzzyEqualXml(root1, root2, absolute, relative):
    return isFuzzyEqualNode(root1, root2, absolute, relative)

# fuzzy compare of XML nodes
def isFuzzyEqualNode(node1, node2, absolute, relative):
    
    for node1child, node2child in zip(node1.iter(), node2.iter()):
        if node1.tag != node2.tag:
            print 'The name of the node differs in ', node1.tag, ' and ', node2.tag
            return False
        if node1.attrib.items() != node2.attrib.items():
            print 'Attributes differ in node ', node1.tag
            return False
        if len(list(node1.iter())) != len(list(node2.iter())):
            print 'Number of children differs in node ', node1.tag
            return False
        if node1child.text or node2child.text:
            if not isFuzzyEqualText(node1child.text, node2child.text, absolute, relative):
                if(node1child.attrib["Name"] == node2child.attrib["Name"]):
                    print 'Data differs in parameter ', node1child.attrib["Name"]
                    return False
                else:
                    print 'Comparing different parameters', node1child.attrib["Name"], ' and ', node2child.attrib["Name"]
                    return False
    return True

# fuzzy compare of text consisting of whitespace separated numbers
def isFuzzyEqualText(text1, text2, absolute, relative):
    list1 = text1.split()
    list2 = text2.split()
    # difference only in whitespace?
    if (list1 == list2):
        return True
    # compare number by number
    for number1, number2 in zip(list1, list2):
        number1 = float(number1)
        number2 = float(number2)
        if (abs(number1 - number2) > absolute 
            and (number2 == 0.0 or abs(abs(number1 / number2) - 1.0) > relative)):
            print 'Difference is too large between', number1, ' and ', number2
            return False
    return True

def sortByName(elem):
    name = elem.get('Name')
    if name:
        try: 
            return str(name)
        except ValueError:
            return ''
    return ''

# sorts attributes of an item and returns a sorted item
def sortAttrs(item, sorteditem):
    attrkeys = sorted(item.keys())
    for key in attrkeys:
        sorteditem.set(key, item.get(key)) 

def sortElements(items, newroot):
    items = sorted(items, key=sortByName)
    items = sorted(items, key=attrgetter('tag'))
 
    # Once sorted, we sort each of the items
    for item in items:
        # Create a new item to represent the sorted version
        # of the next item, and copy the tag name and contents
        newitem = ET.Element(item.tag)
        if item.text and item.text.isspace() == False:
            newitem.text = item.text
 
        # Copy the attributes (sorted by key) to the new item
        sortAttrs(item, newitem)
 
        # Copy the children of item (sorted) to the new item
        sortElements(list(item), newitem)
 
        # Append this sorted item to the sorted root
        newroot.append(newitem) 

# has to sort all Cell and Point Data after the attribute "Name"!
def sortXML(root):
    if(root.tag != "VTKFile"):
        print 'Format is not a VTKFile. Sorting will most likely fail!'
    # create a new root for the sorted tree
    newroot = ET.Element(root.tag)
    # create the sorted copy
    sortAttrs(root, newroot)
    sortElements(list(root), newroot)
    # return the sorted element tree
    return newroot 

# sorts the data by point coordinates so that it is independent of index numbering
# TODO implement me
def orderGrid(root):
    return root

# TODO implement me
def isDifferentGridOrdering(root1, root2):
    points1 = root1.find("Points")
    points2 = root2.find("Points")
    return False

# main program
# handle arguments and print help message
parser = argparse.ArgumentParser(description='Fuzzy compare of two VTK\
    (Visualization Toolkit) files. The files are accepted if for every\
    value the difference is below the absolute error or below the\
    relative error or below both.')
parser.add_argument('vtu_file_1', type=open,
    help='first file to compare')
parser.add_argument('vtu_file_2', type=open,
    help='second file to compare')
parser.add_argument('-r', '--relative', type=float, default=1e-2,
    help='maximum relative error (default=1e-2)')
parser.add_argument('-a', '--absolute', type=float, default=1e-9,
    help='maximum relative error (default=1e-9)')
args = parser.parse_args()

# construct element tree from XML file
root1 = ET.fromstring(args.vtu_file_1.read())
root2 = ET.fromstring(args.vtu_file_2.read())

# sort the vtu file in case nodes appear in different positions
# (minor changes in the output code) returns an element tree
# after the idea of Dale Lane's xmldiff.py
sortedroot1 = sortXML(root1)
sortedroot2 = sortXML(root2)

# sort the vtu file so that the comparison is independent of the
# index numbering (coming e.g. from different grid managers)
if (isDifferentGridOrdering(sortedroot1, sortedroot2)):
    orderedroot1 = orderGrid(sortedroot1)
    orderedroot2 = orderGrid(sortedroot2)
else:
    orderedroot1 = sortedroot1
    orderedroot2 = sortedroot2

# do the fuzzy compare (of the sorted and ordered root)
if (isFuzzyEqualXml(orderedroot1, orderedroot2, args.absolute, args.relative)):
   exit
else:
   exit(1)


