#!/usr/bin/env python

from dune.testtools.metaini import expand_meta_ini, write_configuration_to_ini
from dune.testtools.static_metaini import extract_static_info
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    parser.add_argument('-d', '--dir', help='The directory to put the output in')
    parser.add_argument('-c', '--cmake', action="store_true", help='Set if the script is called from cmake and should return data to it')
    return vars(parser.parse_args())


# analyse the given arguments
args = get_args()

# expand the meta ini files into a list of configurations
configurations = expand_meta_ini(args["ini"])

# initialize a data structure to pass the list of generated ini files to cmake
metaini = {}
metaini["names"] = []  # TODO this should  have underscores!
metaini["labels"] = {}

# extract the static information from the meta ini file
static_info = extract_static_info(args["ini"])

# write the configurations to the file specified in the name key.
for c in configurations:
    # Discard label groups from the data
    if "__LABELS" in c:
        c["__LABELS"] = list(c["__LABELS"].values())
        metaini["labels"][c["__name"]] = c["__LABELS"]
    write_configuration_to_ini(c, metaini, static_info, args)

if args["cmake"]:
    from dune.testtools.cmakeoutput import printForCMake
    printForCMake(metaini)
