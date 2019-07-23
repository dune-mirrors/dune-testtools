#!/usr/bin/env python

"""
A script that extract static variations of a meta ini file to CMake

Communicate the ``[__static]`` section of the meta ini file with
CMake. The ``[__static]`` section contains information about compile
definitions, test labels, and preprocessor guards.
"""
if __name__ == "__main__":

    import argparse
    from dune.testtools.static_metaini import extract_static_info
    from dune.testtools.cmakeoutput import printForCMake

    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
        parser.add_argument('-s', '--section', default="__static", help='The section to treat as the static section (defaults to __static)')
        parser.add_argument('-f', '--file', default=None, help='The filename to write the result into (stdout if omitted)')
        return vars(parser.parse_args())

    # analyse the given arguments
    args = get_args()

    # call the macro
    static = extract_static_info(args["ini"], args['section'], add_guards=True)

    # print to CMake
    printForCMake(static, args['file'])
