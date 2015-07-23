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
from __future__ import absolute_import
from dune_testtools.escapes import exists_unescaped, escaped_split, strip_escapes, count_unescaped, replace_delimited
from dune_testtools.parser import parse_ini_file, CommandToApply
from dune_testtools.writeini import write_dict_to_ini
from dune_testtools.dotdict import DotDict
from copy import deepcopy
from dune_testtools.command import meta_ini_command, CommandType, apply_commands, command_count
from dune_testtools.uniquenames import *
from six.moves import range


def uniquekeys():
    """ define those keys which are special and should always be made unique """
    return ["__name", "__exec_suffix"]


def expand_key(c, keys):
    # first split all given value lists:
    splitted = []
    for k in keys:
        splitted.append(escaped_split(c[k], ","))

    new_ones = [deepcopy(c) for i in range(len(splitted[0]))]
    # now replace all keys correctly:
    for i, k in enumerate(keys):
        for j, config in enumerate(new_ones):
            config[k] = splitted[i][j]
    for conf in new_ones:
        yield conf


@meta_ini_command(name="expand", argc=1, ctype=CommandType.AT_EXPANSION, returnConfigs=True)
def _expand_command(key=None, configs=None):
    retconfigs = []
    for conf in configs:
        retconfigs = retconfigs + list(expand_key(conf, key))
    return retconfigs


def expand_meta_ini(filename, assignment="=", commentChar="#", whiteFilter=None, blackFilter=None, addNameKey=True):
    """ take a meta ini file and construct the set of ini files it defines

    Arguments:
    ----------
    filename : string
        The filename of the meta ini file

    Keyword Arguments:
    ------------------
    assignment : string
        The standard assignment operator
    commentChar: string
        A  character that defines comments. Everything on a line
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
    parse, cmds = parse_ini_file(filename, assignment=assignment, commentChar=commentChar, returnCommands=True)

    # initialize the list of configurations with the parsed configuration
    configurations = [parse]

    # HOOK: PRE_EXPANSION
    apply_commands(configurations, cmds[CommandType.PRE_EXPANSION], all_cmds=cmds)

    # Preprocessing expansion: Sort and group all expand commands by their argument:
    expanddict = {}
    expandlist = []
    for expcmd in cmds[CommandType.AT_EXPANSION]:
        if len(expcmd.args) == 0:
            expandlist.append(CommandToApply("expand", [], [expcmd.key]))
        else:
            if expcmd.args[0] in expanddict:
                expanddict[expcmd.args[0]].append(expcmd.key)
            else:
                expanddict[expcmd.args[0]] = [expcmd.key]
    for ident, keylist in expanddict.items():
        expandlist.append(CommandToApply("expand", [], keylist))
    cmds[CommandType.AT_EXPANSION] = expandlist

    # Now apply expansion through the machinery
    apply_commands(configurations, cmds[CommandType.AT_EXPANSION], all_cmds=cmds)

    # HOOK: POST_EXPANSION
    apply_commands(configurations, cmds[CommandType.POST_EXPANSION], all_cmds=cmds)

    # define functions needed for resolving key-dependent values
    def needs_resolution(d):
        """ whether curly brackets can be found somewhere in the dictionary d """
        for key, value in d.items():
            if exists_unescaped(value, "}") and exists_unescaped(value, "{"):
                return True
        return False

    def check_for_unique(d, k):
        for cta in cmds[CommandType.POST_FILTERING]:
            if (cta.key == k and cta.name == "unique") or (k in uniquekeys()):
                raise ValueError("You cannot have keys depend on keys which are marked unique. This is a chicken-egg situation!")
        return d[k]

    def resolve_key_dependencies(d):
        """ replace curly brackets with keys by the appropriate key from the dictionary - recursively """
        for key, value in d.items():
            while (exists_unescaped(value, "}")) and (exists_unescaped(value, "{")):
                # split the contents form the innermost curly brackets from the rest
                d[key] = replace_delimited(value, d, access_func=check_for_unique)
                value = d[key]

    # HOOK: PRE_RESOLUTION
    apply_commands(configurations, cmds[CommandType.PRE_RESOLUTION], all_cmds=cmds)

    # resolve all key-dependent names present in the configurations
    for c in configurations:
        # values might depend on keys, whose value also depend on other keys.
        # In a worst case scenario concerning the order of resolution,
        # a call to resolve_key_dependencies only resolves one such layer.
        # That is why we need to do this until all dependencies are resolved.
        while needs_resolution(c):
            resolve_key_dependencies(c)

    # HOOK: POST_RESOLUTION
    apply_commands(configurations, cmds[CommandType.POST_RESOLUTION], all_cmds=cmds)

    # HOOK: PRE_FILTERING
    apply_commands(configurations, cmds[CommandType.PRE_FILTERING], all_cmds=cmds)

    # Apply filtering
    if blackFilter:
        # check whether a single filter has been given and make a tuple if so
        if not hasattr(blackFilter, '__iter__'):
            blackFilter = [blackFilter]
    else:
        blackFilter = []

    # always ignore the section called "__local". Its keys by definition do not influence the number of configuration.
    blackFilter = [f for f in blackFilter] + ["__local"]
    # remove all keys that match the given filtering
    configurations = [c.filter([k for k in c if True not in [k.startswith(f) for f in blackFilter]]) for c in configurations]

    if whiteFilter:
        # check whether a single filter has been given and make a tuple if so
        if not hasattr(whiteFilter, '__iter__'):
            whiteFilter = (whiteFilter,)
        # remove all keys that do not match the given filtering
        configurations = [c.filter(whiteFilter) for c in configurations]

    # remove duplicate configurations - we added hashing to the DotDict class just for this purpose.
    configurations = [c for c in sorted(set(configurations))]

    # Implement the naming scheme through the special key __name
    if addNameKey:
        # circumvent the fact, that commands on non-existent keys are ignored
        if "__name" not in configurations[0]:
            configurations[0]["__name"] = ''
        cmds[CommandType.POST_FILTERING].append(CommandToApply(name="unique", args=[], key="__name"))
    else:
        for c in configurations:
            if "__name" in c:
                del c["__name"]

    # HOOK: POST_FILTERING
    apply_commands(configurations, cmds[CommandType.POST_FILTERING])

    # Strip escapes TODO: Which charaters should be escaped not to mess with our code?
    possibly_escaped_chars = "[]{}="
    for c in configurations:
        for k, v in list(c.items()):
            escaped_value = v
            for char in possibly_escaped_chars:
                escaped_value = strip_escapes(escaped_value, char)
            c[k] = escaped_value

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
    if "__static" in c:
        for sc in static_info["__CONFIGS"]:
            if static_info[sc] == c["__static"]:
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
    if ("__static" in c) and (not args["cmake"]):
        del c["__static"]

    write_dict_to_ini(c, fn + "." + extension)
