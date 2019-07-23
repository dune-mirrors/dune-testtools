""" A module formatting data in a way that can be picked up by CMake

.. currentmodule:: dune.testtools.cmakeoutput

The CMakeParseArguments module is a very helpful in processing
data in CMake. This module formats Python data in a way to have it
recognized by CMakeParseArguments through the macro ``parse_python_data``
from ``dune-testtools/cmake/modules/ParsePythonData.cmake``.

Currently the following assumptions on the data are made:

- The data is considered to be a dict. Otherwise naming of the CMake variables
  would be a pain.
- The dictionary can contain dictionaries itself (arbitrarily nested). The keys
  in CMake are appended with an underscore inbetween
- All keys and values must be convertible to strings.

Semicolons in the data need to be replaced by a different character, because
CMake uses semicolons as list separators. The replacement character is passed to CMake
to undo the replacement.
"""
from __future__ import absolute_import
from __future__ import print_function


def printForCMake(d, filename):
    """A function to communicate meta ini information with CMake

        :param d: A dictionary with information to be passed to CMake
        :type d: dict

        .. note::
            You can pass any dictionary to CMake given that the elements
            can be converted to strings. There is no limit on the depth.

    """
    # Do all the error checking in the beginning and forget about it later
    if not isinstance(d, dict):
        raise ValueError("Expected a dictionary for the Python-CMake interface")

    def check_str(x):
        try:
            str(x)
        except ValueError:
            print("All data elements must be convertible to a string")

    def check_dict(a):
        for val in a:
            if isinstance(val, dict):
                check_dict(val)
                continue
            if isinstance(val, list):
                for i in val:
                    if isinstance(i, dict):
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
            if isinstance(val, list):
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
        if s == '':
            return '__empty'
        else:
            return str(s).replace(";", replacement)

    def add_dictionary_to_keys(dic, singlekeys, multikeys, data, prefix=""):
        # add a dictionary to the keys
        for key, value in dict.items(dic):
            if isinstance(value, dict):
                singlekeys, multikeys, data = add_dictionary_to_keys(value, singlekeys, multikeys, data, prefix + str(key) + "_")
                continue
            if isinstance(value, list):
                multikeys = multikeys + prefix + prepare_val(key) + delimiter
                data = data + prefix + prepare_val(key) + delimiter
                for item in value:
                    if (isinstance(item, dict)) or (isinstance(item, list)):
                        raise ValueError("Nesting of complex types not supported")
                    data = data + prepare_val(item) + delimiter
                continue
            singlekeys = singlekeys + prefix + prepare_val(key) + delimiter
            data = data + prefix + prepare_val(key) + delimiter + prepare_val(value) + delimiter
        return [singlekeys, multikeys, data]

    singlekeys, multikeys, data = add_dictionary_to_keys(d, singlekeys, multikeys, data)
    output = singlekeys + multikeys + data
    output = output + "__SEMICOLON" + delimiter + replacement + delimiter

    if filename is None:
        # this is necessary because Python will always add a newline character on program exit
        import sys
        sys.stdout.write(output[:-1])
    else:
        with open(filename, 'w') as f:
            f.write(output[:-1])
