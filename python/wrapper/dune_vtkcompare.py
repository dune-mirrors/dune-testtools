#!/usr/bin/env python

# This is the test wrapper to compare vtu files.

import sys

from dune.testtools.wrapper.argumentparser import get_args
from dune.testtools.wrapper.call_executable import call
from dune.testtools.wrapper.fuzzy_compare_vtk import compare_vtk
from dune.testtools.parser import parse_ini_file


# Parse the given arguments
args = get_args()

# Execute the actual test!
ret = call(args["exec"], args["ini"])

# do the vtk comparison if execution was succesful
if ret is 0:
    # Parse the inifile to learn about where the vtk file and its reference solution are located.
    ini = parse_ini_file(args["ini"])
    try:
        solution = ini["vtk.name"]
        ext = ini.get("vtk.extension", "vtu")
        reference = ini["vtk.reference"]
        ret = compare_vtk(solution + "." + ext, args["source"] + "/" + reference + "." + ext)
    except KeyError:
        sys.stdout.write("The test wrapper vtkcompare assumes keys vtk.name and vtk.reference to be existent in the inifile")
        ret = 1

sys.exit(ret)
