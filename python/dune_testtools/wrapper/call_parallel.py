""" A module that manages the parallel call to C++ executables """
from __future__ import absolute_import

from dune_testtools.wrapper.argumentparser import get_args
from dune_testtools.parser import parse_ini_file
import subprocess
import sys


def call(executable, mpi_exec, mpi_numprocflag, mpi_preflags, mpi_postflags, inifile=None):
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
        if "__num_processes" in iniinfo:
            command[2] = iniinfo["__num_processes"]

    return subprocess.call(command)
