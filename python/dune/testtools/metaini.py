"""A module for expanding meta ini files into sets of ini files.

.. currentmodule:: dune.testtools.metaini

This piece of documentation deals with the meta ini module. For
an better overview what meta ini files are and how they can be useful
we refer to the :ref:`introduction to meta ini files <introductionmetaini>`.
This is an example showing the power of the meta ini syntax:

.. code-block:: ini
   :caption: An example meta ini ini file

    __name = {model.parameters}_gridlevel{grid.level}

    [grid]
    level = 3, 4, 5 | expand out
    screenOutput = 1, 0, 0 | expand out #screen output for level >= 4 kills me

    [model]
    parameters = simple, complex | expand

.. note::

   The example produces a total of 6 ini files.

Commands
++++++++

.. _expand:
.. metaini_command:: expand

    .. metaini_command_arg:: IDENTIFIER
        :single:

        An arbitrary identifier connecting expansion processes of all keys
        that have the same identifier assigned to the `expand` command.

    The command `expand` is the most important command in the meta ini context.
    It expands a given key-value pair of a (parsed) meta ini file into multiple
    ini files where the value of the keys each take one of the comma separated
    values residing in `value`.

    Example:

    In the following code example shows a simple meta ini file using the `expand`
    command.

    .. code-block:: ini

        a = 2, 3, 4 | expand

    .. note::

        The meta ini file will be expanded into 3 ini files

    Assigning multiple keys the `expand` command will result in the combinatoric product.

    .. code-block:: ini

        a = 2, 3, 4 | expand
        b = 1, 2, 3 | expand

    .. note::

        The example produces a total of 9 ini files.

    If an identifier is present behind two or more `expand` commands, those keys will be
    expanded together.

    .. code-block:: ini

        a = 2, 3, 4 | expand bla
        b = 1, 2, 3 | expand bla

    .. note::

        The example produces a total of 3 ini files.

"""
from __future__ import absolute_import
from dune.testtools.parametertree.dotdict import DotDict
from dune.testtools.escapes import exists_unescaped, escaped_split, strip_escapes, count_unescaped, replace_delimited, extract_delimited
from dune.testtools.parser import parse_ini_file, CommandToApply
from dune.testtools.writeini import write_dict_to_ini
from copy import deepcopy
from dune.testtools.command import meta_ini_command, CommandType, apply_commands, command_count
from dune.testtools.uniquenames import *
from six.moves import range


def uniquekeys():
    """ Define those keys which are special and should always be made unique """
    return ["__name", "__exec_suffix"]


def expand_key(c, keys):
    """ Expand a group of keys together

        :param c: A meta ini dictionary
        :type c: dune.testtools.parametertree.dotdict.DotDict
        :param keys: The keys to be expanded together
        :type keys: string

        :returns: A generator for the resulting configurations
        :rtype: generator expression

    """
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
    """Defines the meta ini command expand"""
    retconfigs = []
    for conf in configs:
        retconfigs = retconfigs + list(expand_key(conf, key))
    return retconfigs


def expand_meta_ini(filename, assignment="=", commentChar="#", whiteFilter=None, blackFilter=None, addNameKey=True):
    """
    Take a meta ini file and construct the set of ini files it defines

    Required Arguments:

    :param filename: The filename of the meta ini file
    :type filename:  string

    Optional Arguments:

    :type commentChar:  string
    :param commentChar: A  character that defines comments. Everything on a line
                        after such character is ignored during the parsing process.

    :type whiteFilter:  tuple
    :param whiteFilter: Filter the given keys. The elements of the returned set of
                        configurations will be unique.

    :type blackFilter:  tuple
    :param blackFilter: The standard assignment operator

    :type addNameKey:  bool
    :param addNameKey: Whether a key ``__name`` should be in the output. Defaults to true, where
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

    def check_for_unique(d, k):
        for cta in cmds[CommandType.POST_FILTERING]:
            if (cta.key == k and cta.name == "unique") or (k in uniquekeys()):
                raise ValueError("You cannot have keys depend on keys which are marked unique. This is a chicken-egg situation!")
        return d[k]

    def resolve_key_dependencies(d):
        """ replace curly brackets with keys by the appropriate key from the dictionary - recursively """
        resolved = False
        for key, value in d.items():
            if exists_unescaped(value, "}") and exists_unescaped(value, "{"):
                # Check whether this key has an AT_RESOLUTION command applied
                lookup_key = extract_delimited(value, leftdelimiter="{", rightdelimiter="}")
                if lookup_key in [c.key for c in cmds[CommandType.AT_RESOLUTION]]:
                    continue

                # split the contents form the innermost curly brackets from the rest
                d[key] = replace_delimited(value, d, access_func=check_for_unique)
                resolved = True

        return resolved

    # HOOK: PRE_RESOLUTION
    apply_commands(configurations, cmds[CommandType.PRE_RESOLUTION], all_cmds=cmds)

    # resolve all key-dependent names present in the configurations
    for c in configurations:
        # values might depend on keys, whose value also depend on other keys.
        # In a worst case scenario concerning the order of resolution,
        # a call to resolve_key_dependencies only resolves one such layer.
        # That is why we need to do this until all dependencies are resolved.
        while resolve_key_dependencies(c):
            pass

    # If we have AT_RESOLUTION commands present, we need to reiterate resolution
    # until all of these are resolved!
    at_resolution_commands = cmds[CommandType.AT_RESOLUTION]
    while at_resolution_commands:
        for cmd in cmds[CommandType.AT_RESOLUTION]:
            skip = False
            for c in configurations:
                value = c[cmd.key]

                # If the value still contains curly brackets, we have to skip this!
                if exists_unescaped(value, "}") and exists_unescaped(value, "{"):
                    skip = True

                # If the argument list still contains curly brackets we do the same
                for arg in cmd.args:
                    if exists_unescaped(arg, "}") and exists_unescaped(arg, "{"):
                        argval = c[extract_delimited(arg, leftdelimiter="{", rightdelimiter="}")]
                        if exists_unescaped(argval, "}") and exists_unescaped(argval, "{"):
                            skip = True

            if skip:
                continue

            apply_commands(configurations, [cmd], all_cmds=cmds)
            at_resolution_commands.remove(cmd)

        for c in configurations:
            while resolve_key_dependencies(c):
                pass

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


def write_configuration_to_ini(c, metaini, static_info, args, section='__static', prefix=""):
    """Write a configuration to a file

        Configurations are ini files or meta ini files represented as a dictionary.
        This functions writes such a configuration to an ini file.
    """
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
    if section in c:
        for sc in static_info["__CONFIGS"]:
            if static_info[sc] == c[section]:
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
    # Don't do it, if this is called from CMake to give the user the possibility to understand as much as possible
    # from the expansion process.
    if ("__name" in c) and (not args["cmake"]):
        del c["__name"]
    if ("__exec_suffix" in c) and (not args["cmake"]):
        del c["__exec_suffix"]
    if (section in c) and (not args["cmake"]):
        del c[section]

    write_dict_to_ini(c, fn + "." + extension)
