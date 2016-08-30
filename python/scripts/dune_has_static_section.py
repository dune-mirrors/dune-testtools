#!/usr/bin/env python

"""
A script to check if there are static variations in a meta ini file

To be called by CMake. Provides CMake with information on if a
``[__static]`` section is present in the meta ini file. If no
such section is present, the system test does not contain static
variations and at most one executable has to be generated.

"""
if __name__ == "__main__":

    from dune.testtools.metaini import expand_meta_ini
    import argparse
    import sys

    # define the argument parser for this script
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The inifile', required=True)
    parser.add_argument('-s', '--section', default="__static", help='The section to treat as the static section (defaults to __static)')
    args = vars(parser.parse_args())

    configurations = expand_meta_ini(args['ini'], whiteFilter=(args['section'],), addNameKey=False)
    if len(configurations) > 1:
            sys.exit(1)
    sys.exit(0)
