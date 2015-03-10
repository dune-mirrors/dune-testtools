""" define tools for parsing Dune-style ini files into python

TODO:
- allow values to be lists (as obtained by Dune::FieldVector)
"""

# inspired by http://www.decalage.info/fr/python/configparser

from escapes import escaped_split, exists_unescaped, strip_escapes, count_unescaped, extract_delimited
from dotdict import DotDict

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
    # check whether we have a good assignment character (some projects use spaces here). I drop support
    # for that for the moment, because it makes the code uglier and less readable!
    assert(assignment != " ")

    # choose the type of dictionary to be used depending on whether dots in keys should be interpreted as subgroups
    if subgroups:
        dicttype = DotDict
    else:
        dicttype = dict

    result_dict = dicttype()

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
            # isolate the group name
            group = extract_delimited(line)

            # add a new dictionary for the group name and set the current dict to it
            if not group in result_dict:
                result_dict[group] = dicttype()
            current_dict = result_dict[group]
            continue

        # We dont care about [ and ] from now on, remove the escape characters
        line = strip_escapes(line, "[")
        line = strip_escapes(line, "]")

        # check whether this line defines a key/value pair
        # only process if the assignment string is found exactly once
        # 0 => no relevant assignment 2=> this is actually an assignment with a more complicated operator
        if count_unescaped(line, assignment) is 1:
            # split key from value
            key, value = escaped_split(line, assignment)

            # strip the escapes from assignment characters, they arent special anymore from now on
            for c in assignment:
                value = strip_escapes(value, c)

            # set the dictionary entry
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

    return result_dict

