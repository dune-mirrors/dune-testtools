""" A module for writing ini files to disc """


def write_to_stream(d, stream, assignment="="):
    def traverse_dict(stream, d, prefix):
        # first traverse all non-group values (they would otherwise be considered part of a group)
        for key, value in sorted(dict.items(d)):
            if not isinstance(value, dict):
                stream.write("{} {} {}\n".format(key, assignment, value))

        # now go into subgroups
        for key, value in sorted(dict.items(d)):
            if isinstance(value, dict):
                pre = prefix + [key]

                def groupname(prefixlist):
                    prefix = ""
                    for p in prefixlist:
                        if prefix is not "":
                            prefix = prefix + "."
                        prefix = prefix + p
                    return prefix

                stream.write("\n[{}]\n".format(groupname(pre)))
                traverse_dict(stream, value, pre)

    prefix = []
    traverse_dict(stream, d, prefix)


def write_dict_to_ini(d, filename, assignment="="):
    """ Write a (nested) dictionary to a file following the ini file syntax:

    Arguments:
    ----------
    d : dict
        the dictionary to write
    filename : string
        the filename to write the dict to

    Keyword Arguments:
    ------------------
    assignment : string
        the character(s) which should be used for assigning values to keys
    """
    f = open(filename, 'w')
    write_to_stream(d, f, assignment=assignment)
