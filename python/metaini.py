""" A module for expanding meta ini files into sets of ini files.

This module provides methods to expand a meta ini files into a set
of corresponding ini files. The meta ini file format is defined as
follows.

- The syntax of a regular ini file with "=" as assignment operator for
  key/value pairs is entirely valid. Every ini file is also a meta ini file.
- A user can use an arbitrary amount of additional assignment operators.
  These must be of the form "=<type>=", where <type> is any string identifying
- Such custom assignment operators are followed by a comma separated list of
  values instead of a single value. All assignments using the same operator
  must use the same number of values.
- For each assignment operator present in the meta ini file <n> sets of key/value pairs
  are generated, where <n> is the number of entries in the lists after that
  assignment operator.
- The sets of key/value pairs from different assignment operators are combined
  to larger set by taking the cartesian product of the individual sets.
- The assignment operator "==" (<type> is empty) is special, in the sense,
  that it will always build a product, even with other key/value pairs using "=="
- You can have values depending on other key/value pairs. The syntax for such dependency
  is having a key (use dots for nested keys) in curly brackets inside the value.
  Those values are replaced by the actual value after expanding the meta ini file
  into the set of ini files.
- The output ini files use the meta ini name as a base name. By default, an
  increasing number is appended to the basename.
- You can also set a custom name for the generated ini file by setting the
  reserved key "__name" in your meta ini file and use the {} syntax for meaningful naming.
- The characters '=', ',',' {','}','[' and ']' must be escaped with a backslash in order
  to be used in keys or values. You are even better off avoiding them.

This is an example aiming at showing the full power of the meta ini syntax:

==== START example
__name = {model.parameters}_gridlevel{grid.level}

[grid]
level =grid= 3, 4, 5
screenOutput =grid= 1, 0, 0 #screen output for level >= 4 kills me

[model]
parameters == simple, complex
==== END example

The example produces a total of 6 ini files.

Known issues:
- the code could use a lot more error checking
"""

from escapes import exists_unescaped, escaped_split, strip_escapes, count_unescaped, replace_delimited
from parseini import parse_ini_file
from writeini import write_dict_to_ini
from dotdict import DotDict
from copy import deepcopy
from command import meta_ini_command, CommandType, apply_generic_command
import uniquenames

def uniquekeys():
    """ define those keys which are special and should always be made unique """
    return ["__name", "__exec_suffix"]

def expand_key(c, keys, val, othercommands):
    # first split all given value lists:
    splitted = []
    for v in val:
        splitted.append(escaped_split(v, ","))

    for conf_to_expand in c:
        new_ones = [deepcopy(conf_to_expand) for i in range(len(splitted[0]))]
        # now replace all keys correctly:
        for i, k in enumerate(keys):
            for j, config in enumerate(new_ones):
                config[k] = splitted[i][j] + othercommands[i]
        for conf in new_ones:
            yield conf

@meta_ini_command(name="expand", argc=1, ctype=CommandType.AT_EXPANSION, returnValue=False)
def _expand_command(key=None, value=None, configs=None, args=None, othercommands=""):
    # first check whether this is all product.
    if len(args) == 0:
        configs[:] = [c for c in expand_key(configs, [key], [value], [othercommands])]
    else:
        # collect a list of all keys that use the same identifier
        keys_to_split = []
        vals_to_split = []
        command_list = []
        # configs[0] is the parsed dict
        for key, value in configs[0].items():
            # search for the (first) expand command
            parts = escaped_split(value, delimiter="|")
            partiterator = iter(parts); next(partiterator)
            command = []
            for cmd in partiterator:
                cmdargs = escaped_split(cmd)
                if cmdargs[0] == "expand":
                    command = cmdargs
                    break
            # if we have a simple expand command skip this key
            if len(command) <= 1:
                continue
            # if the expand argument matches, add the key for expansion
            if command[1] == args[0]:
                keys_to_split.append(key)
                vals_to_split.append(parts[0])
                command_list.append(othercommands)

        # Update the list of configurations by expanding one type of assignment
        if len(keys_to_split) > 0:
            configs[:] = [c for c in expand_key(configs, keys_to_split, vals_to_split, command_list)]
    return None

def expand_meta_ini(filename, assignment="=", commentChar=("#",), whiteFilter=None, blackFilter=None, addNameKey=True):
    """ take a meta ini file and construct the set of ini files it defines

    Arguments:
    ----------
    filename : string
        The filename of the meta ini file

    Keyword Arguments:
    ------------------
    assignment : string
        The standard assignment operator
    commentChar: list
        A list of characters that define comments. Everything on a line
        after such character is ignored during the parsing process.
    whiteFilter : tuple
        Filter the given keys. The elements of the returned set of
        configurations will be unique.
    blackFilter : tuple
        Remove the given keys from the output. The elements of the returned set of
        configurations will be unique. If both the whiteFilter and the blackFilter
        option are used, the blackFilter will be applied first.
    addNameKey : bool
        Whether a key __name should be in the output. Defaults to true, where
        a unique name key is generated from the given name key and added to the
        file (even when no generation pattern is given). If set to false, no
        name key will be in the output, whether a scheme was given or not.
    """

    # parse the ini file
    parse = parse_ini_file(filename, assignment=assignment, commentChar=commentChar, asStrings=True)

    # HOOK: POST_PARSE
    for k, v in parse.items():
        apply_generic_command(config=parse, key=k, ctype=CommandType.POST_PARSE)

    # initialize the list of configurations with the parsed configuration
    configurations = [parse]

    # HOOK: PRE_EXPANSION
    for k, v in configurations[0].items():
        apply_generic_command(config=configurations[0], key=k, ctype=CommandType.PRE_EXPANSION)

    # HOOK: AT_EXPANSION
    for k, v in parse.items():
        apply_generic_command(config=parse, key=k, configs=configurations, ctype=CommandType.AT_EXPANSION)

    # HOOK: POST_EXPANSION
    for c in configurations:
        for k, v in c.items():
            apply_generic_command(config=c, key=k, configs=configurations, ctype=CommandType.POST_EXPANSION)

    # define functions needed for resolving key-dependent values
    def needs_resolution(d):
        """ whether curly brackets can be found somewhere in the dictionary d """
        for key, value in d.items():
            if exists_unescaped(value, "}") and exists_unescaped(value, "{"):
                return True
        return False

    def check_for_unique(d, k):
        if exists_unescaped(d[k], "|"):
            cmds = escaped_split(d[k], "|")
            if ("unique" in cmds[1:]) or (k in uniqueKeys()):
                raise ValueError("You cannot have keys depend on keys which are marked unique. This is a chicken-egg situation!")
        return d[k]

    def resolve_key_dependencies(d):
        """ replace curly brackets with keys by the appropriate key from the dictionary - recursively """
        for key, value in d.items():
            while (exists_unescaped(value, "}")) and (exists_unescaped(value, "{")):
                # split the contents form the innermost curly brackets from the rest
                d[key] = replace_delimited(value, d, access_func=check_for_unique)
                value = d[key]

    # resolve all key-dependent names present in the configurations
    for c in configurations:

        # HOOK: PRE_RESOLUTION
        for k, v in c.items():
            apply_generic_command(config=c, key=k, configs=configurations, ctype=CommandType.PRE_RESOLUTION)

        # values might depend on keys, whose value also depend on other keys.
        # In a worst case scenario concerning the order of resolution,
        # a call to resolve_key_dependencies only resolves one such layer.
        # That is why we need to do this until all dependencies are resolved.
        while needs_resolution(c) is True:
            resolve_key_dependencies(c)

        # HOOK: POST_RESOLUTION
        for k, v in c.items():
            apply_generic_command(config=c, key=k, configs=configurations, ctype=CommandType.POST_RESOLUTION)

    for c in configurations:
        for k, v in c.items():
            apply_generic_command(config=c, key=k, configs=configurations, ctype=CommandType.PRE_FILTERING)

    if blackFilter:
        # check whether a single filter has been given and make a tuple if so
        if not hasattr(blackFilter, '__iter__'):
            blackFilter = (blackFilter,)
        # remove all keys that match the given filtering
        configurations = [c.filter([k for k in c if not True in [k.startswith(f) for f in blackFilter]]) for c in configurations]

    if whiteFilter:
        # check whether a single filter has been given and make a tuple if so
        if not hasattr(whiteFilter, '__iter__'):
            whiteFilter = (whiteFilter,)
        # remove all keys that do not match the given filtering
        configurations = [c.filter(whiteFilter) for c in configurations]

    if blackFilter or whiteFilter:
        # remove duplicate configurations (by doing weird and evil stuff because dicts are not hashable)
        configurations = [DotDict(from_str=s) for s in set([str(c) for c in configurations])]

    # Implement the naming scheme through the special key __name
    if addNameKey is True:
        if "__name" not in configurations[0]:
            configurations[0]["__name"] = ""
        configurations[0]["__name"] = configurations[0]["__name"] + " | unique"
    else:
        for c in configurations:
            if "__name" in c:
                del c["__name"]

    for c in configurations:
        for k, v in c.items():
            apply_generic_command(config=c, key=k, configs=configurations, ctype=CommandType.POST_FILTERING)

    return configurations

def write_configuration_to_ini(c, metaini, static_info, args, prefix=""):
    # get the unique ini name
    fn = c["__name"]

    # check if a special inifile extension was given
    if "__inifile_extension" in c:
        extension = c["__inifile_extension"].strip(".")
        del c["__inifile_extension"]
    else:
        # othwise default to .ini
        extension = "ini"

    # append the ini file name to the names list...
    metaini["names"].append(fn + "." + extension)
    # ... and connect it to a exec_suffix
    # This is done by looking through the list of available static configurations and looking for a match.
    # This procedure is necessary because we cannot reproduce the naming scheme for exec_suffixes in the
    # much larger set of static + dynamic variations.
    if "__STATIC" in c:
        for sc in static_info["__CONFIGS"]:
            if static_info[sc] == c["__STATIC"]:
                metaini[prefix + fn + "." + extension + "_suffix"] = sc
    else:
        metaini[prefix + fn + "." + extension + "_suffix"] = ""

    # add an absolute path to the filename
    # this is the folder where files are printed to
    # and manipulate the __name key accordingly
    # the __name key then consists of the path of the actual ini file and a unique name without extension
    if "dir" in args:
        from os import path
        fn = path.basename(fn)
        dirname = args["dir"] or path.dirname(fn)
        fn = path.join(dirname, fn)
        c["__name"] = fn

    # before writing the expanded ini file delete the special keywords to make it look like an ordinary ini file
    # Don't do it, if this is called from cmake to give the user the possibility to understand as much as possible
    # from the expansion process.
    if ("__name" in c) and (not args["cmake"]):
        del c["__name"]
    if ("__exec_suffix" in c) and (not args["cmake"]):
        del c["__exec_suffix"]
    if ("__STATIC" in c) and (not args["cmake"]):
        del c["__STATIC"]

    write_dict_to_ini(c, fn + "." + extension)


# if this module is run as a script, expand a given meta ini file
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    parser.add_argument('-d', '--dir', help='The directory to put the output in')
    parser.add_argument('-c', '--cmake', action="store_true", help='Set if the script is called from cmake and should return data to it')
    args = vars(parser.parse_args())

    # expand the meta ini files into a list of configurations
    configurations = expand_meta_ini(args["ini"])

    # initialize a data structure to pass the list of generated ini files to cmake
    metaini = {}
    metaini["names"] = []  # TODO this should  have underscores!

    # extract the static information from the meta ini file
    from static_metaini import extract_static_info
    static_info = extract_static_info(args["ini"])

    # write the configurations to the file specified in the name key.
    for c in configurations:
        write_configuration_to_ini(c, metaini, static_info, args)

    if args["cmake"]:
        from cmakeoutput import printForCMake
        printForCMake(metaini)
