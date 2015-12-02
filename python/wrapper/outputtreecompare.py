#!/usr/bin/env python

# This is the test wrapper to compare output ini files

import sys

from dune.testtools.wrapper.argumentparser import get_args
from dune.testtools.wrapper.call_executable import call
from dune.testtools.wrapper.compare_ini import compare_ini, fuzzy_compare_ini
from dune.testtools.parser import parse_ini_file


# Parse the given arguments
args = get_args()

# Execute the actual test!
ret = call(args["exec"], args["ini"])

# do the outputtree comparison if execution was succesful
if ret is 0:
    # Parse the inifile to learn about where the output file and its reference are located.
    ini = parse_ini_file(args["ini"])
    try:
        # get reference solutions
        names = ini["wrapper.outputtreecompare.name"].split(' ')
        exts = ini.get("wrapper.outputtreecompare.extension", "out " * len(names)).split(' ')
        references = ini["wrapper.outputtreecompare.reference"].split(' ')
    except KeyError:
        sys.stdout.write("The test wrapper outputtreecompare assumes keys wrapper.outputtreecompare.name \
                          and wrapper.outputtreecompare.reference to be existent in the inifile")

    # loop over all outputtree comparisons
    for n, e, r in zip(names, exts, references):
        # if we have multiple vtks search in the subgroup prefixed with the vtk-name for options
        prefix = "" if len(names) == 1 else n + "."

        # check for specific options for this comparison
        checktype = float(ini.get("wrapper.outputtreecompare." + prefix + "type", "exact"))
        exclude = ini.get("wrapper.outputtreecompare." + prefix + "exclude", [])

        # fuzzy comparisons
        if checktype == "fuzzy":
            relative = float(ini.get("wrapper.outputtreecompare." + prefix + "relative", 1.0e-2))
            absolute = float(ini.get("wrapper.outputtreecompare." + prefix + "absolute", 1.5e-7))
            zeroThreshold = ini.get("wrapper.outputtreecompare." + prefix + "zeroThreshold", {})

            ret = fuzzy_compare_ini(inifile1=n + "." + e,
                                    inifile2=args["source"] + "/" + r + "." + e,
                                    absolute=absolute,
                                    relative=relative,
                                    zeroValueThreshold=zeroThreshold,
                                    exclude=exclude,
                                    verbose=True)

            # early exit if one vtk comparison fails
            if ret is not 0:
                sys.exit(ret)

        # exact comparison
        else:
            ret = compare_ini(inifile1=n + "." + e,
                              inifile2=args["source"] + "/" + r + "." + e,
                              exclude=exclude,
                              verbose=True)

sys.exit(0)
