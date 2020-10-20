#!/usr/bin/env python

"""
Test wrapper for parallel execution of a simulation and subsequent comparison
of vtu files.

This test wrapper executes a given simulation in parallel and (given successful
execution) compares the produced vtu/vtp/vtk files to reference files, that
were provided at a sane state of the code.

To be used in the CMake system test macro as follows:

.. code-block:: cmake

    dune_add_system_test(...
                         SCRIPT dune_execute_parallel.py
                         ...)

The wrapper is a combination of the 'dune_execute_parallel.py' and
'dune_vtkcompare.py' wrappers. The wrapper can be configured through the meta
ini file by specifying the corresponding sections for above wrappers:

.. code-block:: ini

    [wrapper.execute_parallel]
    numprocesses = 8

    [wrapper.vtkcompare]
    name = myvtkfile
    reference = path_to_reference_file
    extension = vtu
    relative = 1e-2
    absolute = 1.2e-7
    zeroThreshold.velocity = 1e-18
    timestep = 100

Check the documentation of those wrappers for a detailed description of the
options. The filenames for the output files of the parallel simulation must
be configured in the meta ini file and passed as a space separated list.
"""


if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.call_executable import call_parallel
    from dune.testtools.wrapper.fuzzy_compare_vtk import compare_vtk
    from dune.testtools.parser import parse_ini_file

    # Parse the given arguments
    args = get_args()
    if not args["mpi_exec"]:
        sys.stderr.write("call_parallel.py: error: Mpi executable not given.\n" +
                         "usage: call_parallel.py [-h] -e EXEC -i INI --mpi-exec MPI_EXEC \n" +
                         "                        --mpi-numprocflag MPI_NUMPROCFLAG [-s SOURCE]\n")
        sys.exit(1)
    if not args["mpi_numprocflag"]:
        sys.stderr.write("call_parallel.py: error: Mpi number of processes flag not given.\n" +
                         "usage: call_parallel.py [-h] -e EXEC -i INI --mpi-exec MPI_EXEC \n" +
                         "                         --mpi-numprocflag MPI_NUMPROCFLAG [-s SOURCE]\n")
        sys.exit(1)

    # check if flags are provided
    if args["mpi_preflags"] == ['']:
        args["mpi_preflags"] = None
    if args["mpi_postflags"] == ['']:
        args["mpi_postflags"] = None

    ret = call_parallel(args["exec"], args["mpi_exec"], args["mpi_numprocflag"], args["mpi_preflags"], args["mpi_postflags"], args['max_processors'][0], inifile=args["ini"])

    # do the vtk comparison if execution was succesful
    if ret is 0:
        # Parse the inifile to learn about where the vtk files and its reference solutions are located.
        ini = parse_ini_file(args["ini"])
        try:
            # get reference solutions
            names = ini["wrapper.vtkcompare.name"].split(' ')
            timestep = ini.get("wrapper.vtkcompare.timestep", "")
            if timestep:
                timestep = "-" + str(timestep).zfill(5)
            exts = ini.get("wrapper.vtkcompare.extension", "vtu " * len(names)).split(' ')
            references = ini["wrapper.vtkcompare.reference"].split(' ')
        except KeyError:
            sys.stdout.write("The test wrapper vtkcompare assumes keys wrapper.vtkcompare.name \
                              and wrapper.vtkcompare.reference to be existent in the inifile")
        # loop over all vtk comparisons
        for n, e, r in zip(names, exts, references):
            # keys may be set for each vtk (in a subsection with its name) or for all of them
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

