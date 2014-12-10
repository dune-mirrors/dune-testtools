""" define tools for parsing Dune-style ini files into python

TODO:
- allow values to be lists (as obtained by Dune::FieldVector)
"""

# inspired by http://www.decalage.info/fr/python/configparser

from escapes import *

def parse_ini_file(filename, commentChar=("#",), assignment="=", asStrings=False, conversionList=(int, float,), subgroups=True):
    """ parse Dune style .ini files into a dictionary

    The parser behaviour can be customized by the keyword arguments of this function.
    The dictionary contains nested dictionaries according to nested subgroups in the
    ini file.

    Keyword arguments:
    ------------------
    commentChar: list
        A list of characters that define comments. Everything on a line
        after such character is ignored during the parsing process.
    assignment : string
        A string that separates the key from the value on a line
        containing a key/value pair.
    asStrings : bool
        Whether the values should be treated as strings.
    conversionList : list
        A list of functions to try for converting the parsed strings to other types
        The order of the functions defines the priority of the conversion rules
        (highest priority first). All conversion rules are expected to raise
        a ValueError when they are not applicable.
    subgroups : bool
        Whether the file should be parsed as containing subgroups
    """
    result_dict = {}
    f = open(filename)
    current_dict = result_dict
    for line in f:
        # strip the endline character
        line = line.strip("\n")

        # strip comments from the line
        for char in commentChar:
            if exists_unescaped(line, char):
                line, comment = escaped_split(line, char, 1)
            # all other occurences can be handled normally now
            line = strip_escapes(line, char)

        # check whether this line specifies a group
        if (exists_unescaped(line,"[")) and (exists_unescaped(line,"]")):
            # reset the current dictionary
            current_dict = result_dict

            # isolate the group name
            group, bracket = escaped_split(line, "]", 1)
            bracket, group = escaped_split(group, "[", 1)
            group = group.strip(" ")

            # process the stack of subgroups given
            if subgroups is True:
                while exists_unescaped(group,"."):
                    subgroup, group = escaped_split(group, ".", 1)
                    if subgroup not in current_dict:
                        current_dict[subgroup] = {}
                    current_dict = current_dict[subgroup]

            # add a new dictionary for the group name and set the current dict to it
            if group not in current_dict:
                current_dict[group] = {}
            current_dict = current_dict[group]
            continue

        # We dont care about [ and ] from now on, remove the escape characters
        line = strip_escapes(line, "[")
        line = strip_escapes(line, "]")

        print "Line after group detection: {}".format(line)

        # save the current_dict to reset it after each key/value pair evaluation
        # this is necessary to have some subgroup definitions in keys instead of in square brackets.
        group_dict = current_dict

        # check whether this line defines a key/value pair
        # only process if the assignment string is found exactly once
        # 0 => no relevant assignment 2=> this is actually an assignment with a more complicated operator
        if (count_unescaped(line, assignment) is 1) or ((assignment is " ") and (line.count(assignment) is not 0)):
            # split key from value
            if assignment is " ":
                key, value = line.split(" ", 1)
            else:
                key, value = escaped_split(line, assignment)

            print "Key, value: {} {}".format(key, value)

            # look for additional groups in the key
            key = key.strip()
            if subgroups is True:
                # dots in group names cannot be escaped. Otherwise, we will end up in HELL.
                while "." in key:
                    group, key = key.split(".")
                    if group not in current_dict:
                        current_dict[group] = {}
                    current_dict = current_dict[group]

            # strip blanks from the value
            value = value.strip()
            for c in assignment:
                value = strip_escapes(value, c)

            # set the dictionary entry for this pair to the default string
            if key is not "":
                current_dict[key] = value

                # check whether a given conversion applies to this key
                if not asStrings:
                    # iterate over the list of conversion functions in reverse priority order
                    for rule in [x for x in reversed(conversionList)]:
                        try:
                            current_dict[key] = rule(value)
                        except ValueError:
                            pass

        # restore the current dictionary to the current group
        current_dict = group_dict

    return result_dict

