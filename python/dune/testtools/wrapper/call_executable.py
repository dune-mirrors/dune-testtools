""" A module that manages the call to C++ executables """
from __future__ import absolute_import

from dune.testtools.parser import parse_ini_file
import subprocess


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
