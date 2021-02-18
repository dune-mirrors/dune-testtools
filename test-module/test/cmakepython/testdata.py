from dune.testtools.cmakeoutput import printForCMake
import sys

# define a rather complex data structure to pass to CMake
d = {}
# simple keys with different combinations of key and value types
d[3] = "5"
d[2] = 17
d[8] = [4, "something"]
d["mykey"] = ["bla", "blubb"]
d["nested"] = {}
d["nested"]["bla"] = "val"
d["nested"][5] = {}
d["nested"][5]["deeper"] = "wow!"

""" d should produce the following variables in CMake:
TESTPREFIX_3
TESTPREFIX_2
TESTPREFIX_8
TESTPREFIX_mykey
TESTPREFIX_nested_bla
TESTPREFIX_nested_5_deeper
"""

printForCMake(d, sys.argv[1])
