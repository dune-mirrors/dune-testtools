#!/usr/bin/env python

"""
A test wrapper to compare output ini files.

The test wrapper compares an ini file that is produced by the simulation
with a reference file that was produced at a sane state of the code.
Ini files as output can be easily used to write out any kind of information
with ``dune-testtools`` using the ``Dune::OutputTree`` class.

To be used in the CMake system test macro as follows

.. code-block:: cmake

    dune_add_system_test(...
                         SCRIPT dune_outputtreecompare.py
                         ...)

The wrapper can be configured through the meta ini file under the section
``[wrapper.outputtreecompare]`` with the following options

.. code-block:: ini

    [wrapper.outputtreecompare]
    name = myoutputfile
    reference = path_to_reference_file
    extension = out
    type = exact / fuzzy
    exclude = rubbishkey
    relative = 1e-2
    absolute = 1.5e-7
    zeroThreshold.norm = 1e-18

The mandatory parameters are ``name`` and ``reference``. ``name`` specifies
the name of the produced file with a path relative to the executables build directory.
``reference`` specifies the name of the reference file with a path relative to the
tests source directory. The ``extension`` parameter defaults to ``out``. The comparison
can be done ``exact`` (not recommend if data contains floating point numbers) or in
a ``fuzzy`` comparison. The ``fuzzy`` comparison compares all values that are convertible
to a floating point number with a ``relative`` and ``absolute`` epsilon (optionally the
relative and/or absolute epsilon can be specified). The ``zeroThreshold`` parameter sets a value for a certain
key in the ini file (here "norm") under which the value is considered exact 0.
Values under the threshold (given that both reference and current solution are under the
threshold) will thus be excluded from comparison. This is useful if a parameter suffers
from numerical noise. Keys can be completely excluded from comparison specifying the
exclude key. Exclude takes a space separated list.

The wrapper can also handle multiple ini comparisons.

.. code-block:: ini

    [wrapper.outputtreecompare]
    name = out1 out2
    reference = path_to_reference_file1 path_to_reference_file2
    extension = out out

    [wrapper.outputtreecompare.out1]
    type = exact
    exclude = bla

    [wrapper.outputtreecompare.out2]
    type = fuzzy
    zeroThreshold.norm = 1e-18

In this case the parameters ``type``, ``exclude``, ``relative``, ``absolute``, and ``zeroThreshold`` can be
set for each test separately under the sections ``[wrapper.outputtreecompare.<name>]``.
"""
if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.call_executable import call
    from dune.testtools.wrapper.compareini import compare_ini, fuzzy_compare_ini
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
            checktype = ini.get("wrapper.outputtreecompare." + prefix + "type", "exact")
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

    sys.exit(ret)
