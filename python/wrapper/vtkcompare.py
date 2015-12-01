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
    # Parse the inifile to learn about where the vtk files and its reference solutions are located.
    ini = parse_ini_file(args["ini"])
    try:
        # get reference solutions
        names = ini["wrapper.vtkcompare.name"].split(' ')
        exts = ini.get("wrapper.vtkcompare.extension", "vtu " * len(names)).split(' ')
        references = ini["wrapper.vtkcompare.reference"].split(' ')
    except KeyError:
        sys.stdout.write("The test wrapper vtkcompare assumes keys wrapper.vtkcompare.name \
                          and wrapper.vtkcompare.reference to be existent in the inifile")

    # loop over all vtk comparisons
    for n, e, r in zip(names, exts, references):
        # if we have multiple vtks search in the subgroup prefixed with the vtk-name for options
        prefix = "" if len(names) == 1 else n + "."

        # check for specific options for this comparison
        relative = float(ini.get("wrapper.vtkcompare." + prefix + "relative", 1e-2))
        absolute = float(ini.get("wrapper.vtkcompare." + prefix + "absolute", 1.5e-7))
        zeroThreshold = ini.get("wrapper.vtkcompare." + prefix + "zeroThreshold", {})

        ret = compare_vtk(vtk1=n + "." + e,
                          vtk2=args["source"] + "/" + r + "." + e,
                          absolute=absolute,
                          relative=relative,
                          zeroValueThreshold=zeroThreshold,
                          verbose=True)

        # early exit if one vtk comparison fails
        if ret is not 0:
            sys.exit(ret)

sys.exit(0)
