#!/usr/bin/env python

"""
A test wrapper to compare vtu files.

The test wrapper compares a vtu/vtp/vtk file that is produced by the simulation
with a reference file that was produced at a sane state of the code.

To be used in the CMake system test macro as follows

.. code-block:: cmake

    dune_add_system_test(...
                         SCRIPT dune_vtkcompare.py
                         ...)

The wrapper can be configured through the meta ini file under the section
``[wrapper.vtkcompare]`` with the following options

.. code-block:: ini

    [wrapper.vtkcompare]
    name = myvtkfile
    reference = path_to_reference_file
    extension = vtu
    relative = 1e-2
    absolute = 1.2e-7
    zeroThreshold.velocity = 1e-18
    timestep = 100

The mandatory parameters are ``name`` and ``reference``. ``name`` specifies
the name of the produced file with a path relative to the executables build directory.
``reference`` specifies the name of the reference file with a path relative to the
tests source directory. The ``extension`` parameter defaults to ``vtu``. The parameters
``relative``, ``absolute`` set the epsilons for relative, absolute floating point
comparison respectively. The ``zeroThreshold`` parameter sets a value for a certain
data array in the vtu file (here "velocity") under which the value is considered exact 0.
Values under the threshold (given that both reference and current solution are under the
threshold) will thus be excluded from comparison. This is useful if a parameter suffers
from numerical noise. The ``timestep`` parameter can be used if VTK data is written
through a VTKSequenceWriter instance and only the results at the given time should be
considered for the VTK comparison.

.. note::
    The vtk comparison also works when the grid manager uses different indices than
    the grid manager used for the reference file. The vtk file gets sorted with respect
    to the grid coordinates.

The wrapper can also handle multiple vtu comparison for e.g. multidomain tests where a
vtu file is written for each domain. The vtu files are to be given as space separated list

.. code-block:: ini

    [wrapper.vtkcompare]
    name = myvtkfile1 myvtkfile2
    reference = path_to_reference_file1 path_to_reference_file2
    extension = vtu vtu
    relative = 1e-3
    absolute = 1.5e-7
    zeroThreshold.velocity = 1e-18

    [wrapper.vtkcompare.myvtkfile1]
    relative = 1e-2
    zeroThreshold.velocity = 1e-18

In this case the parameters ``relative``, ``absolute``, and ``zeroThreshold`` may be
set for each test separately under the sections ``[wrapper.vtkcompare.<name>]``.

If the programm needs to be run in parallel, the desired number of processes
needs to be specified in an additional section:

.. code-block:: ini

    [wrapper.vtkcompare]
    name = myvtkfile1 myvtkfile2
    reference = path_to_reference_file1 path_to_reference_file2
    extension = vtu vtu
    relative = 1e-3
    absolute = 1.5e-7
    zeroThreshold.velocity = 1e-18

    [wrapper.vtkcompare.parallel]
    numprocesses = 8
"""


if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.call_executable import call
    from dune.testtools.wrapper.call_executable import call_parallel
    from dune.testtools.wrapper.call_executable import check_mpi_arguments
    from dune.testtools.wrapper.fuzzy_compare_vtk import compare_vtk
    from dune.testtools.parser import parse_ini_file

    # Parse the given arguments
    args = get_args()

    # parse ini file
    ini = parse_ini_file(args["ini"])

    # execute the application either in parallel or sequentially, depending
    # on whether the number of processors was specified in the meta ini file.
    ret = 1

    if "wrapper.vtkcompare.parallel.numprocesses" in ini:

        check_mpi_arguments(args)

        ret = call_parallel(
            args["exec"],
            args["mpi_exec"],
            args["mpi_numprocflag"],
            args["mpi_preflags"],
            args["mpi_postflags"],
            args['max_processors'][0],
            inifile=args["ini"])
    else:
        ret = call(args["exec"], args["ini"])

    # do the vtk comparison if execution was succesful
    if ret is 0:
        try:
            # get reference solutions
            names = ini["wrapper.vtkcompare.name"].split(' ')
            timestep = ini.get("wrapper.vtkcompare.timestep", "")
            if timestep:
                timestep = "-" + str(timestep).zfill(5)
            exts = ini.get(
                "wrapper.vtkcompare.extension",
                "vtu " * len(names)).split(' ')
            references = ini["wrapper.vtkcompare.reference"].split(' ')
        except KeyError:
            sys.stdout.write(
                "The test wrapper vtkcompare assumes keys wrapper.vtkcompare.name \
                              and wrapper.vtkcompare.reference to be existent in the inifile")

        # loop over all vtk comparisons
        for n, e, r in zip(names, exts, references):
            # keys may be set for each vtk (in a subsection with its name) or
            # for all of them
            def get_key(key):
                if "wrapper.vtkcompare." + n + "." + key in ini:
                    return "wrapper.vtkcompare." + n + "." + key
                else:
                    return "wrapper.vtkcompare." + key

            # check for specific options for this comparison
            relative = float(ini.get(get_key("relative"), 1e-2))
            absolute = float(ini.get(get_key("absolute"), 1.2e-7))
            zeroThreshold = ini.get(get_key("zeroThreshold"), {})

            ret = compare_vtk(vtk1=n + timestep + "." + e,
                              vtk2=args["source"] + "/" + r + "." + e,
                              absolute=absolute,
                              relative=relative,
                              zeroValueThreshold=zeroThreshold,
                              verbose=True)

            # early exit if one vtk comparison fails
            if ret is not 0:
                sys.exit(ret)

    sys.exit(ret)
