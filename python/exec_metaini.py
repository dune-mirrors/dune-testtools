from compile_definitions import extract_compile_definitions
from metaIni import expand_meta_ini
from writeIni import write_dict_to_ini
import sys

if (len(sys.argv) is 2):
    # expand the meta ini files into a list of configurations
    configurations = expand_meta_ini(sys.argv[1])

    # here, we can modify the configurations, look for special keys,
    # extract information and do all sorts of weird stuff.

    # extract compile definitions from all the ini files that we got
    static_confs, indices = extract_compile_definitions(configurations)

    # map compile definitions to executable suffixes
    exec_suffix = {}
    exec_suffix[""] = ""
    for i, c in enumerate(configurations):
        if "__exec_suffix" in c:
            if (static_confs[indices[i]] in exec_suffix) and (exec_suffix[static_confs[indices[i]]] != c["__exec_suffix"]):
                raise Error("Found two static configurations with different suffixes")
            else:
                exec_suffix[static_confs[indices[i]]] = c["__exec_suffix"]
        else:
            if len(static_confs) > 1:
                raise KeyError("At the moment, all inis are expected to have an __exec_suffix key (if they have static information)")

    # cook up something to return to cmake
    returndef = ""
    for sc in static_confs:
        if returndef != "":
            returndef = returndef + "\n"
        returndef = returndef + exec_suffix[sc] + ";" + sc

    # write the configurations to the file specified in the name key.
    for c in configurations:
        fn = c["__name"]
        del c["__name"]
        write_dict_to_ini(c, fn)

    # This print statement is for cmake to read the standard output of this script.
    # Ideally, this feature is enabled through an optional parameter to this script (TODO)
    print returndef


else:
    print "exec_metaIni expects exactly one command line parameter: the meta ini file"
