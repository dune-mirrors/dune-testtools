from metaIni import expand_meta_ini
from cmakeoutput import printForCMake
import sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
args = vars(parser.parse_args())

static_section = expand_meta_ini(args["ini"], filterKeys=["__STATIC", "__exec_suffix"], addNameKey=False)

# determine a list of subgroups within the static section
static_groups = []
for conf in static_section:
    # check for __STATIC section. Who knows who may call this without having the section in the metaini-file
    if "__STATIC" in conf:
        for key in conf["__STATIC"]:
            if (type(conf["__STATIC"][key]) is dict) and (key not in static_groups):
                static_groups.append(key)
    else:
        # debug output
        sys.stderr.write("\n -- Static variant generation failed because no __STATIC section could be found in the meta-inifile!\n")

# construct a dictionary from the static information. This can be passed to CMake
static = {}
# only pass a dictionary to CMake if there is more than one target to be build
if(len(static_section) > 1):
    # The special key __CONFIGS holds a list of configuration names
    static["__CONFIGS"] = []
    # introduce a special key for all subgroups
    for group in static_groups:
        static["__" + group] = []

    generic_exec_suffix = 0

    for conf in static_section:
        # check for __exec_suffix keyword
        if "__exec_suffix" in conf:
            # take the configuration name and add it to the data
            static["__CONFIGS"].append(conf["__exec_suffix"])

            # check for key/value pairs in subgroups and add lists to the dictionary
            for group in static_groups:
                for key in conf["__STATIC"][group]:
                    if key not in static["__" + group]:
                        static["__" + group].append(key)

            # copy the entire data
            static[conf["__exec_suffix"]] = conf["__STATIC"]
        else:
            # append an integer
            # TODO this assumes either no suffixes are given or all. otherwise (rare) there could be name clashes
            static["__CONFIGS"].append(str(generic_exec_suffix))
            generic_exec_suffix += 1

    # print to CMake
    printForCMake(static)
