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
- Having semicolons in the data would be a PAIN (cmake hell + escape hell = a hell of a hell)
"""

def printForCMake(d):
    if type(d) is not dict:
        raise ValueError("Expected a dict")

    # CMake expects a list and CMake lists use semicolons as delimiters
    delimiter = ";"

    singlekeys = "__SINGLE" + delimiter
    multikeys = "__MULTI" + delimiter
    data = "__DATA" + delimiter

    for key, value in d.items():
        if type(value) is dict:
            raise ValueError("Nested dicts are not supported")
        if type(value) is list:
            multikeys = multikeys + str(key) + delimiter
            data = data + str(key) + delimiter
            for item in value:
                if (type(item) is dict) or (type(item) is list):
                    raise ValueError("Nesting of complex types not supported")
                data = data + str(item) + delimiter
        else:
            singlekeys = singlekeys + str(key) + delimiter
            data = data + str(key) + delimiter + str(value) + delimiter

    output = singlekeys + multikeys + data

    # this is necessary because python will always add a newline character on program exit
    import sys
    sys.stdout.write(output[:-1])

d = {}
d["bla"] = "mafai"
d["bli"] = [1, 2, 3]
printForCMake(d)

