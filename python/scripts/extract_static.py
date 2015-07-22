#!/usr/bin/env python

import argparse
from dune_testtools.static_metaini import extract_static_info
from dune_testtools.cmakeoutput import printForCMake


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    return vars(parser.parse_args())


# analyse the given arguments
args = get_args()

# call the macro
static = extract_static_info(args["ini"])

# print to CMake
printForCMake(static)
