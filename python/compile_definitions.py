""" A module extracting a set of compile definitions from an ini file

TODO the exact interface will evolve with the implementation
"""

def def_string(d, groupkey="__STATIC"):
    """ form a compile definitions string as taken by the cmake
    build system from a sub dictionary """
    definition = ""
    if groupkey in d:
        # extract the dictionary with the static information
        s = d[groupkey]
        for key, value in s.items():
            # if there is already stuff, first append the cmake list delimiter
            if len(definition) > 0:
                # TODO make this nicer
                # using '&' as a separator is hopefully helpful with cmake list hell!
                definition = definition + "&"
            # TODO find out what needs to escaped in order to correctly get this
            # through cmake and the c preprocessor
            definition = definition + key.upper() + "=" + value
    return definition

def extract_compile_definitions(confs, groupkey="__STATIC"):
    """ Extract a set of compile definitions from an ini file

    Returns a list of static configurations and a list of indices,
    which maps the ini files to their static configurations.

    Arguments:
    ----------
    confs : list of dicts
        The list of dictionaries representing the ini file

    Keyword Arguments:
    ------------------
    groupkey : string
        The group key that contains the static information
    """

    # define a list with all the compile definition configurations found
    static_confs = []
    # define a list that maps the configurations to their compile definition (by indexing in above list)
    indices = []

    for c in confs:
        # compute the compile definition for this configuration...
        definition = def_string(c, groupkey)
        # ... and lookup whether this definition was already found
        if definition in static_confs:
            indices.append(static_confs.index(definition))
        else:
            indices.append(len(static_confs))
            static_confs.append(definition)

    # return the collected information
    return static_confs, indices
