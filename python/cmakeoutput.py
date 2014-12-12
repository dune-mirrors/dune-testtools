""" A module formatting data in a way that can be picked up by CMake

The CMakeParseArguments module is a VERY helpful in processing
data in CMake. This module formats python data in a way to have it
recognized by CMakeParseArguments through the macro parse_python_data
from dune-testtools/cmake/modules/ParsePythonData.cmake .

Currently the assumptions on the data given to printForCMake are strong,
but it is very helpful anyway:

- The data is considered to be a dict. Otherwise naming of the cmake variables
  would be a pain.
- All values in the dict must either be lists or values convertible to a string.
- All items in such lists must themselves be convertible to a string (no lists).

Semicolons in the data pose a major problem here: CMake uses semicolons as a list
delimiter. The naive attempt to escape them did not work. They are therefore
substituted by a different character which is not present in the data and that
character is passed to CMake too. Any better ideas to do this are welcome, it feels
like a hack.
"""

def printForCMake(d):
    # Do all the error checking in the beginning and forget about it later
    if type(d) is not dict:
        raise ValueError("Expected a dict")
    def check_str(x):
        try:
            str(x)
        except ValueError:
            print "All data elements must be convertible to a string"
    for val in d:
        if type(val) is list:
            for i in val:
                check_str(i)
        else:
            check_str(val)

    # Treat the general problem of semicolons being list separators in CMake.
    # set a delimiter for the tokens of our output (there is probably non solution but ";")
    delimiter = ";"
    # find a character that is ASCII, has no special meaning in CMake and does not appear in the data
    specialChars = ["&", "#", "!", "?", "/"]
    def does_not_appear(d, c):
        for val in d:
            if type(val) is list:
                for i in val:
                    if c in str(i):
                        return False
            else:
                if c in str(val):
                    return False
        return True

    replacement = ""
    for c in specialChars:
        if does_not_appear(d, c):
            replacement = c
            break
        raise ValueError("Did not find a proper replacement for the semicolon in the data")

    singlekeys = "__SINGLE" + delimiter
    multikeys = "__MULTI" + delimiter
    data = "__DATA" + delimiter

    def prepare_val(s):
        return str(s).replace(";", replacement)

    for key, value in d.items():
        if type(value) is list:
            multikeys = multikeys + prepare_val(key) + delimiter
            data = data + prepare_val(key) + delimiter
            for item in value:
                if (type(item) is dict) or (type(item) is list):
                    raise ValueError("Nesting of complex types not supported")
                data = data + prepare_val(item) + delimiter
        else:
            singlekeys = singlekeys + prepare_val(key) + delimiter
            data = data + prepare_val(key) + delimiter + prepare_val(value) + delimiter

    output = singlekeys + multikeys + data
    if replacement != "":
        output = output + "__SEMICOLON" + delimiter + replacement + delimiter

    # this is necessary because python will always add a newline character on program exit
    import sys
    sys.stdout.write(output[:-1])
