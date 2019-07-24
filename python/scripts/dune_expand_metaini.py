#!/usr/bin/env python

"""
A script that expands a given meta ini file into its configurations (ini files).

Main interface from Python to CMake. To be called from CMake to obtain all
build system specific information in meta ini files, e.g. information for a
given test which executable to use with which ini file. This script also
controles the expansion process of a single meta ini file into a set of ini files.

"""
if __name__ == "__main__":

    from dune.testtools.metaini import expand_meta_ini, write_configuration_to_ini
    from dune.testtools.static_metaini import extract_static_info
    import argparse

    def get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
        parser.add_argument('-d', '--dir', help='The directory to put the output in')
        parser.add_argument('-c', '--cmake', action="store_true", help='Set if the script is called from CMake and should return data to it')
        parser.add_argument('-s', '--section', default="__static", help='The section to treat as the static section (defaults to __static)')
        parser.add_argument('-f', '--file', default=None, help='The filename to write the result into (stdout if omitted)')
        return vars(parser.parse_args())

    # analyse the given arguments
    args = get_args()

    # expand the meta ini files into a list of configurations
    configurations = expand_meta_ini(args["ini"])

    # initialize a data structure to pass the list of generated ini files to CMake
    metaini = {}
    metaini["names"] = []  # TODO this should  have underscores!
    metaini["labels"] = {}

    # extract the static information from the meta ini file
    static_info = extract_static_info(args["ini"], section=args['section'])

    # write the configurations to the file specified in the name key.
    for c in configurations:
        # Discard label groups from the data
        if "__LABELS" in c:
            c["__LABELS"] = list(c["__LABELS"].values())
            metaini["labels"][c["__name"]] = c["__LABELS"]
        write_configuration_to_ini(c, metaini, static_info, args, section=args['section'])

    if args["cmake"]:
        from dune.testtools.cmakeoutput import printForCMake
        printForCMake(metaini, args['file'])
