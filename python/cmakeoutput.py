""" A module formatting data in a way that can be picked up by CMake

The CMakeParseArguments module is a VERY helpful in processing
data in CMake. This module formats python data in a way to have it
recognized by CMakeParseArguments through the macro parse_python_data
from dune-testtools/cmake/modules/ParsePythonData.cmake .

Currently the following assumptions on the data are made:

- The data is considered to be a dict. Otherwise naming of the cmake variables
  would be a pain.
- The dictionary can contain dictionaries itself (arbitrarily nested). The keys
  in CMake are appended with an underscore inbetween
- All keys and values must be convertible to strings.

Semicolons in the data need to be replaced by a different character, because
CMake does use semicolons as list separators. The replacement is passed to CMake
to undo the replacement.
"""

def printForCMake(d):
    # Do all the error checking in the beginning and forget about it later
    if type(d) is not dict:
        raise ValueError("Expected a dictionary for the Python-CMake interface")
    def check_str(x):
        try:
            str(x)
        except ValueError:
            print "All data elements must be convertible to a string"
    def check_dict(a):
        for val in a:
            if type(val) is dict:
                check_dict(val)
                continue
            if type(val) is list:
                for i in val:
                    if type(i) is dict:
                        raise ValueError("No dictionaries in lists allowed for the Python-CMake interface")
                    check_str(i)
                continue
            check_str(val)
    check_dict(d)

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
