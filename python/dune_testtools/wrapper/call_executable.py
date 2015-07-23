""" A module that manages the call to C++ executables """
from __future__ import absolute_import

from dune_testtools.wrapper.argumentparser import get_args
from dune_testtools.parser import parse_ini_file
import subprocess


def call(executable, inifile=None):
    # If we have an inifile, parse it and look for special keys that modify the execution
    command = ["./" + executable]
    if inifile:
        iniargument = inifile
        iniinfo = parse_ini_file(inifile)
        if "__inifile_optionkey" in iniinfo:
            command.append(iniinfo["__inifile_optionkey"])
        command.append(iniargument)

    return subprocess.call(command)
