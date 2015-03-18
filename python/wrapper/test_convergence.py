from parseIni import parse_ini_file
import os
import sys

def call(inifile):
    # get the convergence test info from the meta ini file

    # calculate the rate according to the outputted data

    # compare the rate 

    return 0

# This is also used as the standard wrapper by cmake
if __name__ == "__main__":
    # Parse the given arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    args = vars(parser.parse_args())

    sys.exit(call(args["ini"]))