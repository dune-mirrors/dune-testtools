""" A module that manages the call to C++ executables """
from __future__ import absolute_import

import sys

from dune.testtools.parser import parse_ini_file
import subprocess


# helper function for handling the MPI arguments. Pass args here, as we
# potentially need to modify it
def check_mpi_arguments(args):

    if not args["mpi_exec"]:
        sys.stderr.write(
            "call_parallel.py: error: Mpi executable not given.\n" +
            "usage: call_parallel.py [-h] -e EXEC -i INI --mpi-exec MPI_EXEC \n" +
            "                        --mpi-numprocflag MPI_NUMPROCFLAG [-s SOURCE]\n")
        sys.exit(1)

    if not args["mpi_numprocflag"]:
        sys.stderr.write(
            "call_parallel.py: error: Mpi number of processes flag not given.\n" +
            "usage: call_parallel.py [-h] -e EXEC -i INI --mpi-exec MPI_EXEC \n" +
            "                         --mpi-numprocflag MPI_NUMPROCFLAG [-s SOURCE]\n")
        sys.exit(1)

    # check if flags are provided
    if args["mpi_preflags"] == ['']:
        args["mpi_preflags"] = None
    if args["mpi_postflags"] == ['']:
        args["mpi_postflags"] = None


def call(executable, inifile=None):
    # If we have an inifile, parse it and look for special keys that modify the execution
    command = [executable]
    if inifile:
        iniargument = inifile
        iniinfo = parse_ini_file(inifile)
        if "__inifile_optionkey" in iniinfo:
            command.append(iniinfo["__inifile_optionkey"])
        command.append(iniargument)

    return subprocess.call(command)


def call_parallel(executable, mpi_exec, mpi_numprocflag, mpi_preflags, mpi_postflags, max_processors, inifile=None):
    # If we have an inifile, parse it and look for special keys that modify the execution
    num_processes = "2"  # a default
    command = [mpi_exec, mpi_numprocflag, num_processes]
    if mpi_preflags:
        command += mpi_preflags
    command += [executable]
    if mpi_postflags:
        command += mpi_postflags
    if inifile:
        iniargument = inifile
        iniinfo = parse_ini_file(inifile)
        if "__inifile_optionkey" in iniinfo:
            command.append(iniinfo["__inifile_optionkey"])
        command.append(iniargument)
        if "wrapper.execute_parallel.numprocesses" in iniinfo:
            command[2] = iniinfo["wrapper.execute_parallel.numprocesses"]

    if int(command[2]) <= int(max_processors):
        return subprocess.call(command)
    else:
        return 77
