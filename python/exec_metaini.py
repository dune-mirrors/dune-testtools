from compile_definitions import extract_compile_definitions
from metaIni import expand_meta_ini
from writeIni import write_dict_to_ini
from cmakeoutput import printForCMake
import sys

if (len(sys.argv) is 2):
    # expand the meta ini files into a list of configurations
    configurations = expand_meta_ini(sys.argv[1])

    # here, we can modify the configurations, look for special keys,
    # extract information and do all sorts of weird stuff.
    static_section = expand_meta_ini(sys.argv[1], filterKeys=["__STATIC", "__exec_suffix"], addNameKey=False)

    # determine a list of subgroups within the static section
    static_groups = []
    for conf in static_section:
        for key in conf["__STATIC"]:
            if (type(conf["__STATIC"][key]) is dict) and (key not in static_groups):
                static_groups.append(key)

    # construct a dictionary from the static information. This can be passed to CMake
    # The special key __CONFIGS holds a list of configuration names
    static = {}
    static["__CONFIGS"] = []
    # introduce a special key for all subgroups
    for group in static_groups:
        static["__" + group] = []

    for conf in static_section:
        # take the configuration name and add it to the data
        static["__CONFIGS"].append(conf["__exec_suffix"])

        # check for key/value pairs in subgroups and add lists to the dictionary
        for group in static_groups:
            for key in conf["__STATIC"][group]:
                if key not in static["__" + group]:
                    static["__" + group].append(key)

        # copy the entire data
        static[conf["__exec_suffix"]] = conf["__STATIC"]

    # print to CMake
    printForCMake(static)

    # TODO add a command line option parser to disable writing configurations

    # write the configurations to the file specified in the name key.
    for c in configurations:
        fn = c["__name"]
        del c["__name"]
        write_dict_to_ini(c, fn)

else:
    print "exec_metaIni expects exactly one command line parameter: the meta ini file"
