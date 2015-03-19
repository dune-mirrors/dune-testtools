""" A module for fuzzy comparing VTK files.

This module provides methods to compare two VTK files. Applicable
for all VTK style formats like VTK files. Fuzzy compares numbers by
using absolute and/or relative difference comparison.

"""

import argparse
import xml.etree.ElementTree as ET
from operator import attrgetter
import sys

# fuzzy compare VTK tree from VTK strings
def compare_vtk(vtk1, vtk2, absolute=1e-9, relative=1e-2):
    """ take two vtk files and compare them. Returns an exit key as returnvalue.

    Arguments:
    ----------
    vtk1, vtk2 : string
        The filenames of the vtk files to compare

    Keyword Arguments:
    ------------------
    absolute : float
        The epsilon used for comparing numbers with an absolute criterion
    relative: float
        The epsilon used for comparing numbers with an relative criterion
    """

    # construct element tree from vtk file
    root1 = ET.fromstring(open(vtk1).read())
    root2 = ET.fromstring(open(vtk2).read())

    # sort the vtk file in case nodes appear in different positions
    # e.g. because of minor changes in the output code
    sortedroot1 = sort_vtk(root1)
    sortedroot2 = sort_vtk(root2)

    # sort the vtk file so that the comparison is independent of the
    # index numbering (coming e.g. from different grid managers)
    sortedroot1, sortedroot2 = sort_vtk_by_coordinates(sortedroot1, sortedroot2)

    # do the fuzzy compare
    if is_fuzzy_equal_node(sortedroot1, sortedroot2, absolute, relative):
        return 0
    else:
        return 1

# fuzzy compare of VTK nodes
def is_fuzzy_equal_node(node1, node2, absolute, relative):
    
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
            if not is_fuzzy_equal_text(node1child.text, node2child.text, absolute, relative):
                if(node1child.attrib["Name"] == node2child.attrib["Name"]):
                    print 'Data differs in parameter ', node1child.attrib["Name"]
                    return False
                else:
                    print 'Comparing different parameters', node1child.attrib["Name"], ' and ', node2child.attrib["Name"]
                    return False
    return True

# fuzzy compare of text (in the xml sense) consisting of whitespace separated numbers
def is_fuzzy_equal_text(text1, text2, absolute, relative):
    list1 = text1.split()
    list2 = text2.split()
    # difference only in whitespace?
    if (list1 == list2):
        return True
    # compare number by number
    for number1, number2 in zip(list1, list2):
        number1 = float(number1)
        number2 = float(number2)
        print(abs(abs(number1 / number2) - 1.0))
        print(relative)
        if not number2 == 0.0:
            # check for the relative difference
            if number2 == 0.0 or abs(abs(number1 / number2) - 1.0) > relative:
                print 'Relative difference is too large between', number1, ' and ', number2
                return False
        else:
            # check for the absolute difference
            if abs(number1 - number2) > absolute:
                print 'Absolute difference is too large between', number1, ' and ', number2
                return False
    return True

def sort_by_name(elem):
    name = elem.get('Name')
    if name:
        try: 
            return str(name)
        except ValueError:
            return ''
    return ''

# sorts attributes of an item and returns a sorted item
def sort_attributes(item, sorteditem):
    attrkeys = sorted(item.keys())
    for key in attrkeys:
        sorteditem.set(key, item.get(key)) 

def sort_elements(items, newroot):
    items = sorted(items, key=sort_by_name)
    items = sorted(items, key=attrgetter('tag'))
 
    # Once sorted, we sort each of the items
    for item in items:
        # Create a new item to represent the sorted version
        # of the next item, and copy the tag name and contents
        newitem = ET.Element(item.tag)
        if item.text and item.text.isspace() == False:
            newitem.text = item.text
 
        # Copy the attributes (sorted by key) to the new item
        sort_attributes(item, newitem)
 
        # Copy the children of item (sorted) to the new item
        sort_elements(list(item), newitem)
 
        # Append this sorted item to the sorted root
        newroot.append(newitem) 

# has to sort all Cell and Point Data after the attribute "Name"!
def sort_vtk(root):
    if(root.tag != "VTKFile"):
        print 'Format is not a VTKFile. Sorting will most likely fail!'
    # create a new root for the sorted tree
    newroot = ET.Element(root.tag)
    # create the sorted copy
    # (after the idea of Dale Lane's xmldiff.py)
    sort_attributes(root, newroot)
    sort_elements(list(root), newroot)
    # return the sorted element tree
    return newroot 

# sorts the data by point coordinates so that it is independent of index numbering
def sort_vtk_by_coordinates(root1, root2):
    if is_different_grid_order(root1, root1):
        # TODO implement me
        return (root1, root2)
    else:
        return (root1, root2)

def is_different_grid_order(root1, root2):
    # TODO implement me
    points1 = root1.find("Points")
    points2 = root2.find("Points")
    return False

# main program if called as script return appropriate error codes
if __name__ == "__main__":
    # handle arguments and print help message
    parser = argparse.ArgumentParser(description='Fuzzy compare of two VTK\
        (Visualization Toolkit) files. The files are accepted if for every\
        value the difference is below the absolute error or below the\
        relative error or below both.')
    parser.add_argument('vtk_file_1', type=str, help='first file to compare')
    parser.add_argument('vtk_file_2', type=str, help='second file to compare')
    parser.add_argument('-r', '--relative', type=float, default=1e-2, help='maximum relative error (default=1e-2)')
    parser.add_argument('-a', '--absolute', type=float, default=1e-9, help='maximum absolute error (default=1e-9)')
    args = vars(parser.parse_args())

    sys.exit(compare_vtk(args["vtk_file_1"], args["vtk_file_2"], args["absolute"], args["relative"]))
