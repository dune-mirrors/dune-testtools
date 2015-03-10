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

Known bugs:
- Having special assignment and a subgrouping by keyname in the same line is broken, if that
subgroup is not used elsewhere. THe reason is that the dictionary "normal" doesnt pick it up
correctly.
"""

from escapes import exists_unescaped, escaped_split, strip_escapes, count_unescaped, replace_delimited
from parseIni import parse_ini_file
from writeIni import write_dict_to_ini
from copy import deepcopy

def expand_meta_ini(filename, assignment="=", commentChar=("#",), subgroups=True, filterKeys=None, addNameKey=True):
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
    subgroups : bool
        Whether the meta ini file interprets dots in groups as subgroups
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

    # one dictionary to hold the results from several parser runs
    # the keys are all the types of assignments occuring in the file
    # except for normal assignment, which is treated differently.
    result = {}

    # we always have normal assignment
    normal = parse_ini_file(filename, assignment=assignment, asStrings=True, subgroups=subgroups)

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
                result[assignChar] = {}

    # look into the file to determine the set of assignment operators used
    get_assignment_operators(filename, result)

    # get dictionaries for all sorts of assignments
    for key in result:
        assignChar = "{}{}{}".format(assignment, key, assignment)
        result[key] = parse_ini_file(filename, assignment=assignChar, asStrings=True, subgroups=subgroups)

    # apply the filtering of groups if needed
    if filterKeys is not None:
        # check whether a single filter has been given and make a list if so
        if type(filterKeys) is not list:
            filterKeys = [filterKeys]
        # remove all keys that do not match the given filtering
        for key, value in normal.items():
            if key not in filterKeys:
                del normal[key]
        for char, assignType in result.items():
            for key,value in assignType.items():
                if key not in filterKeys:
                    del result[char][key]

     # start combining dictionaries - there is always the normal dict...
    configurations = [normal]

    # ...except we deleted all keys with the filter. If all dictionaries are empty
    # because of the filtering, we are done and return the configurations
    all_dictionaries_empty = True
    for char, assignType in result.items():
        if assignType.items():
            all_dictionaries_empty = False
    if normal:
        all_dictionaries_empty = False

    if all_dictionaries_empty:
        return configurations

    def generate_configs(d, configurations, prefix=[]):
        def configs_for_key(key, vals, configs, prefix):
            for config in configs:
                for val in vals:
                    c = deepcopy(config)
                    pos = c
                    for p in prefix:
                        pos = pos[p]
                    pos[key] = val
                    yield c

        for key, values in d.items():
            if type(values) is dict:
                pref = prefix + [key]
                configurations = generate_configs(values, configurations, pref)
            else:
                values = escaped_split(values, ',')
                configurations = configs_for_key(key, values, configurations, prefix)

        for config in configurations:
            yield config

    # do the all product part associated with the == assignment
    if "" in result:
        configurations = [l for l in generate_configs(result[""], configurations)]

    def expand_dict(d, output=None, prefix=[]):
        """ expand the dictionary of one assignment operator into a set of dictionary
            containing the actual key value pairs of that assignment operator """
        for key, values in d.items():
            if type(values) is dict:
                pref = prefix + [key]
                output = expand_dict(values, output, pref)
            else:
                values = escaped_split(values, ',')
                if output is None:
                    output = [{} for i in range(len(values))]
                for index, val in enumerate(values):
                    mydict = output[index]
                    for p in prefix:
                        if p not in mydict:
                            mydict[p] = {}
                        mydict = mydict[p]
                    mydict[key] = val

        return output

    def join_nested_dicts(d1, d2):
        """ join two dictionaries recursively """
        for key, item in d2.items():
            if type(item) is dict:
                d1[key] = join_nested_dicts(d1[key], item)
            else:
                d1[key] = item
        return d1

    # do the part for all other assignment operators
    for assign, tree in result.items():
        # ignore the one we already did above
        if assign is not "":
            expanded_dict = expand_dict(tree)

            newconfigurations = []

            # combine the expanded dictionaries with the ones in configurations
            for config in configurations:
                for newpart in expanded_dict:
                    # newconfigurations.append(dict(config.items() + newpart.items()))
                    newconfigurations.append(join_nested_dicts(deepcopy(config), newpart))

            configurations = newconfigurations

    # resolve all key-dependent names present in the configurations
    for c in configurations:

        def needs_resolution(d):
            """ whether curly brackets can be found somewhere in the dictionary d """
            for key, value in d.items():
                if type(value) is dict:
                    if needs_resolution(value) is True:
                        return True
                else:
                    if exists_unescaped(value, "}") and exists_unescaped(value, "{"):
                        return True
            return False

        def dotkey(d, key):
            """ Given a key containing dots, return the value from a nested dictionary """
            if "." in key:
                group, key = escaped_split(key, ".", 1)
                return dotkey(d[group], key)
            else:
                return d[key]

        def resolve_key_dependencies(fulldict, processdict):
            """ replace curly brackets with keys by the appropriate key from the dictionary - recursively """
            for key, value in processdict.items():
                if type(value) is dict:
                    resolve_key_dependencies(fulldict, value)
                else:
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

    # Implement the naming scheme through the special key __name
    if addNameKey is True:
        # count the number of occurences of __name keys in the data set
        name_dict = {}
        for c in configurations:
            if "__name" in c:
                if c["__name"] not in name_dict:
                    name_dict[c["__name"]] = 1
                else:
                    name_dict[c["__name"]] += 1

        # now delete all those keys that occur once and reset all others to a counter
        for key, value in name_dict.items():
            if value is 1:
                del name_dict[key]
            else:
                name_dict[key] = 0

        # initialize a counter in the case of number only file name generation
        counter = 0
        base, extension = filename.split(".", 1)
        for conf in configurations:
            # check whether a custom name has been provided by the user
            if "__name" in conf:
                conffile = "_" + conf["__name"]
                if conf["__name"] in name_dict:
                    conffile += "_" + str(name_dict[conf["__name"]]).zfill(4)
                    name_dict[conf["__name"]] += 1
                # update the name key in the configuration dictionary
                conf["__name"] = base + conffile
            else:
                conf["__name"] = base + str(counter).zfill(4)
                counter = counter + 1
    # if no naming scheme is to be implemented, remove all __name keys
    else:
        for c in configurations:
            if "__name" in c:
                del c["__name"]

    return configurations

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

    # write the configurations to the file specified in the name key.
    for c in configurations:
        fn = c["__name"]

        # check if a special inifile extension was given
        if "__inifile_extension" in c:
            extension = c["__inifile_extension"].strip(".")
            del c["__inifile_extension"]
        else:
            # othwise default to .ini
            extension = "ini"

         # check if a special inifile option key was given
        if "__inifile_optionkey" in c:
            ini_optionkey = c["__inifile_optionkey"]
            del c["__inifile_optionkey"]
        else:
            # othwise default to empty string
            ini_optionkey = ""

        # append the ini file name to the names list...
        metaini["names"].append(fn + "." + extension)
        # ... and connect it to a exec_suffix
        # get static variants to determine executable suffix
        static_section = expand_meta_ini(args["ini"], filterKeys=["__STATIC", "__exec_suffix"], addNameKey=False)
        if not(len(static_section) > 1):
            # no static variation. No suffix, target gets the basename
            metaini[fn + "." + extension + "_suffix"] = None
        elif "__exec_suffix" in c:
            # exec_suffix specifies user defined target names
            metaini[fn + "." + extension + "_suffix"] = c.get("__exec_suffix", "")
        else:
            # target are generically numbered
            generic_exec_suffix = 0
            for conf in static_section:
                #if the static sections are equal the right suffix is determined by the generic suffix
                if conf["__STATIC"] == c["__STATIC"]:
                    metaini[fn + "." + extension + "_suffix"] = str(generic_exec_suffix)
                generic_exec_suffix += 1

        # ... and to an option key
        metaini[fn + "." + extension + "_optionkey"] = ini_optionkey
        del c["__name"]
        # maybe add an absolute path to the filename
        if "dir" in args:
            from os import path
            fn = path.basename(fn)
            dirname = args["dir"] or path.dirname(fn)
            fn = path.join(dirname, fn)

        # before writing the expanded ini file delete the special keywords
        # (TODO and static section?) to make it look like an ordinary ini file
        if "__exec_suffix" in c:
            del c["__exec_suffix"]
        # if "__STATIC" in c:
        #     del c["__STATIC"]

        write_dict_to_ini(c, fn + "." + extension)

    if args["cmake"]:
        from cmakeoutput import printForCMake
        printForCMake(metaini)
