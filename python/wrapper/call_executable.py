""" A module that manages the call to C++ executables """

from parseIni import parse_ini_file
import os

def call(executable, inifile=None):
    # If we have an inifile, parse it and look for special keys that modify the execution
    iniargument = ""
    if inifile:
        iniargument = inifile
        iniinfo = parse_ini_file(inifile)
        if "__inifile_optionkey" in iniinfo:
            iniargument = iniinfo["__inifile_optionkey"] + " " + iniargument

    return os.system("./" + executable + " " + iniargument)

# This is also used as the standard wrapper by cmake
if __name__ == "__main__":
    # Parse the given arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exec', help='The executable', required=True)
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    args = vars(parser.parse_args())

    import sys
    sys.exit(call(args["exec"], args["ini"]))
