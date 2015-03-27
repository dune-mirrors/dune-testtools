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
from parseIni import parse_ini_file
from writeIni import write_dict_to_ini
from dotdict import DotDict
from copy import deepcopy
from uniquenames import make_key_unique
from command import meta_ini_command, CommandType, apply_generic_command

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

@meta_ini_command(name="expand", argc=1, ctype=CommandType.AT_EXPANSION)
def _expand_command(key=None, value=None, configs=None, args=None, othercommands=""):
    print "Call mit key={}, value={}, configs={}, args={}, othercommands={}".format(key, value, configs, args, othercommands)
    # first check whether this is all product.
    if len(args) == 0:
        return [c for c in expand_key(configs, [key], [value], [othercommands])]
    else:
        return None
#         for key, value in configs[0].items():
#             # determine whether this value needs splitting
#             splitted = escaped_split(value, delimiter="|", maxsplit=2)
#             tosplit = splitted[0] if exists_unescaped(splitted[0], ",") else None

            # only do something if it does:
#            if tosplit:
#             # check whether a split identifier is given
#             if identifier:
#                 # and whether that given split identifier has already been processed
#                 if not identifier in already_done:
#                     already_done.append(identifier)
#                     # collect a list of all keys that use the same identifier
#                     keys_to_split = []
#                     vals_to_split = []
#                     command_list = []
#                     for k, v in parse.items():
#                         val, ident, oc = split_expand_command(v)
#                         if ident == identifier:
#                             keys_to_split.append(k)
#                             vals_to_split.append(val)
#                             command_list.append(oc)
#
#                     configurations = [c for c in expand_key(configurations, keys_to_split, vals_to_split, command_list)]

def expand_meta_ini(filename, assignment="=", commentChar=("#",), filterKeys=None, addNameKey=True):
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
    filterKeys : string
        Only apply the algorithm to a set of keys given.
        Defaults to None, which means that all groups are taken into account.
        This is white list filtering (explicitly give the keys you want).
    addNameKey : bool
        Whether a key __name should be in the output. Defaults to true, where
        a unique name key is generated from the given name key and added to the
        file (even when no generation pattern is given). If set to false, no
        name key will be in the output, whether a scheme was given or not.
    """

    parse = parse_ini_file(filename, assignment=assignment, commentChar=commentChar, asStrings=True)

#
#     def split_expand_command(s):
#         # only values that contain a pipe can in theory need expanding
#         if exists_unescaped(s, '|'):
#             # split into value, command and additional potentially additional commands
#             splitted = escaped_split(s, '|', maxsplit=2)
#             # extract the string for the command with the highest precedence
#             cmdstr = splitted[1]
#             # and split it into command name plus arguments
#             cmdargs = escaped_split(cmdstr)
#             # check whether the command name is 'expand'
#             if cmdargs[0] == "expand":
#                 assert(len(cmdargs) <= 2)
#                 # return a tuple of the value, the splitting identifier, and possible other commands
#                 return (splitted[0], cmdargs[1] if len(cmdargs) == 2 else None, " | " + splitted[2] if len(splitted)==3 else "")
#         return (None, None, None)
#
#     def expand_key(c, keys, val, othercommands):
#         # first split all given value lists:
#         splitted = []
#         for v in val:
#             splitted.append(escaped_split(v, ","))
#
#         for conf_to_expand in c:
#             new_ones = [deepcopy(conf_to_expand) for i in range(len(splitted[0]))]
#             # now replace all keys correctly:
#             for i, k in enumerate(keys):
#                 for j, config in enumerate(new_ones):
#                     config[k] = splitted[i][j] + othercommands[i]
#             for conf in new_ones:
#                 yield conf
#
#     already_done = []
#     configurations = [parse]
#     for key, value in parse.items():
#         # determine whether this value needs splitting
#         tosplit, identifier, othercommands = split_expand_command(value)
#
#         # only do something if it does:
#         if tosplit:
#             # check whether a split identifier is given
#             if identifier:
#                 # and whether that given split identifier has already been processed
#                 if not identifier in already_done:
#                     already_done.append(identifier)
#                     # collect a list of all keys that use the same identifier
#                     keys_to_split = []
#                     vals_to_split = []
#                     command_list = []
#                     for k, v in parse.items():
#                         val, ident, oc = split_expand_command(v)
#                         if ident == identifier:
#                             keys_to_split.append(k)
#                             vals_to_split.append(val)
#                             command_list.append(oc)
#
#                     configurations = [c for c in expand_key(configurations, keys_to_split, vals_to_split, command_list)]
#             else:
#                 configurations = [c for c in expand_key(configurations, [key], [tosplit], [othercommands])]

    configurations = [parse]
    for k, v in parse.items():
        apply = apply_generic_command(key=k, value=v, configs=configurations, ctype=CommandType.AT_EXPANSION)
        if apply:
            configurations = apply

    print configurations

    # resolve all key-dependent names present in the configurations
    for c in configurations:

        def needs_resolution(d):
            """ whether curly brackets can be found somewhere in the dictionary d """
            for key, value in d.items():
                if exists_unescaped(value, "}") and exists_unescaped(value, "{"):
                    return True
            return False

        def resolve_key_dependencies(fulldict, processdict):
            """ replace curly brackets with keys by the appropriate key from the dictionary - recursively """
            for key, value in processdict.items():
                while (exists_unescaped(value, "}")) and (exists_unescaped(value, "{")):
                    # define a function that replaces the "identity access" d,k -> d[k] when we look for keys
                    def treat_special_keys(d, key):
                        if key.startswith("__lower."):
                            return d[escaped_split(key, ".", maxsplit=1)[1]].lower()
                        if key.startswith("__upper."):
                            return d[escaped_split(key, ".", maxsplit=1)[1]].upper()
                        return d[key]

                    # split the contents form the innermost curly brackets from the rest
                    processdict[key] = replace_delimited(value, fulldict, access_func=treat_special_keys)
                    value = processdict[key]

        # values might depend on keys, whose value also depend on other keys.
        # In a worst case scenario concerning the order of resolution,
        # a call to resolve_key_dependencies only resolves one such layer.
        # That is why we need to do this until all dependencies are resolved.
        while needs_resolution(c) is True:
            resolve_key_dependencies(c, c)

    # apply the filtering of groups if needed
    if filterKeys:
        # check whether a single filter has been given and make a list if so
        if not isinstance(filterKeys, list):
            filterKeys = [filterKeys]
        # remove all keys that do not match the given filtering
        for c in configurations:
            for key, value in c.items():
                if not True in [key.startswith(f) for f in filterKeys]:
                    del c[key]
        # remove duplicate configurations (by doing weird and evil stuff because dicts are not hashable)
        import ast
        configurations = [DotDict(ast.literal_eval(s)) for s in set([str(c) for c in configurations])]

    # Implement the naming scheme through the special key __name
    if addNameKey is True:
        base, extension = filename.split(".", 1)
        make_key_unique(configurations, "__name")
        for conf in configurations:
            conf["__name"] = base + "_" + conf["__name"]
            # cut the underscore in the corner case of exactly one configuration
            if conf["__name"][-1] == "_":
                conf["__name"] = conf["__name"][:-1]

    # if no naming scheme is to be implemented, remove all __name keys
    else:
        for c in configurations:
            if "__name" in c:
                del c["__name"]

    return configurations

def parse_meta_ini_file(filename, assignment="=", commentChar=("#",)):
    # one dictionary to hold the results from several parser runs
    # the keys are all the types of assignments occuring in the file
    # except for normal assignment, which is treated differently.
    result = {}

    # we always have normal assignment
    normal = parse_ini_file(filename, assignment=assignment, asStrings=True)

    def get_assignment_operators(filename, result):
        file = open(filename)
        for line in file:
            # strip comments from the line
            for char in commentChar:
                if exists_unescaped(line, char):
                    line, comment = escaped_split(line, char, 1)
                # all other occurences can be handled normally now
                line = strip_escapes(line, char)
            # get the assignment operators
            if count_unescaped(line, assignment) is 2:
                key, assignChar, value = escaped_split(line, assignment)
                result[assignChar] = DotDict()

    # look into the file to determine the set of assignment operators used
    get_assignment_operators(filename, result)

    # get dictionaries for all sorts of assignments
    for key in result:
        assignChar = "{}{}{}".format(assignment, key, assignment)
        result[key] = parse_ini_file(filename, assignment=assignChar, asStrings=True)

    return (normal, result)

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
