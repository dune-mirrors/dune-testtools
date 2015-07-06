""" A module that implements functionality to makes values in dicts unique within a list of dicts

This is needed to implement the naming of ini files and static configurations alike. There,
a naming scheme might be given, but it may not be unique.
"""

from command import meta_ini_command, CommandType
from escapes import escaped_split

@meta_ini_command(name="unique", ctype=CommandType.POST_FILTERING, returnValue=False)
def make_key_unique(configs=None, key=None):
    # first count the number of occurences of the values
    key_dict = {}
    for c in configs:
        # If the key isnt even in the dict, add it as "" to allow a numbered scheme
        if key not in c:
            c[key] = ""
        if c[key] not in key_dict:
            key_dict[c[key]] = 1
        else:
            key_dict[c[key]] += 1

    # Now delete all those that appeared only once (those are unique already) and reset all the others to 0
    for k, count in key_dict.items():
        if count is 1:
            del key_dict[k]
        else:
            key_dict[k] = 0

    # Now make the values unique
    for c in configs:
        # Check whether this value was found multiple times. If so, it has to be made unique.
        if c[key] in key_dict:
            # increase the counter in key_dict for the given key
            key_dict[c[key]] += 1

            # check whether we have numbering only (doesnt need an underscore)
            if c[key] == "":
                c[key] = str(key_dict[""] - 1).zfill(4)
            else:
                c[key] = c[key] + "_" + str(key_dict[c[key]] - 1).zfill(4)
