#!/usr/bin/env python

"""
A script that extract static variations of a meta ini file to CMake
"""
if __name__ == "__main__":

    import argparse
    from dune.testtools.static_metaini import extract_static_info
    from dune.testtools.cmakeoutput import printForCMake

    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
        return vars(parser.parse_args())

    # analyse the given arguments
    args = get_args()

    # call the macro
    static = extract_static_info(args["ini"], add_guards=True)

    # print to CMake
    printForCMake(static)
