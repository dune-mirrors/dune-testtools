""" A module defining a command to import other meta ini files within meta ini files. 

TODO:
Non trivial options such as a change in assignment character cannot be passed to this command, at the moment.
"""

from parseIni import parse_ini_file
from command import meta_ini_command, CommandType

@meta_ini_command(name="import", argc=1, ctype=CommandType.POST_PARSE)
def _import_ini_file(config=None, key=None, args=None):
    imp = parse_ini_file(args[0])
    for k in imp:
        if k not in config:
            config[k] = imp[k]
    # to simplify piping commands, return the value associated with the key.
    return config[key]