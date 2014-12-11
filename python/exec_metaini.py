from compile_definitions import extract_compile_definitions
from metaIni import expand_meta_ini
from writeIni import write_dict_to_ini
import sys

if (len(sys.argv) is 2):
    # expand the meta ini files into a list of configurations
    configurations = expand_meta_ini(sys.argv[1])

    # here, we can modify the configurations, look for special keys,
    # extract information and do all sorts of weird stuff.
    static_confs, indices = extract_compile_definitions(configurations)

    # write the configurations to the file specified in the name key.
    for c in configurations:
        fn = c["__name"]
        del c["__name"]
        write_dict_to_ini(c, fn)

else:
    print "exec_metaIni expects exactly one command line parameter: the meta ini file"
