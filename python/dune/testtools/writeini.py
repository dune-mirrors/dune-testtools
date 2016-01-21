""" A module converting dicts representing ini files

.. currentmodule:: dune.testtools.writeini

This module provides functions to write a dictionary representing
an ini file to a stream or to file (ini file).

"""


def write_to_stream(d, stream, assignment="="):
    """Write a dictionary to stream in ini file syntax

        :param d: The dictionary representing an ini file
        :type d: DotDict, dict
        :param stream: The stream to write to
        :type stream: string
        :param assignment: The assignment operator used to connect key and value in the stream
        :type assignment: single character

    """
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

        :param d: The dictionary representing an ini file
        :type d: DotDict, dict
        :param filename: The filename of the ini file
        :type filename: string
        :param assignment: The assignment operator used to connect key and value in the stream
        :type assignment: single character
    """
    f = open(filename, 'w')
    write_to_stream(d, f, assignment=assignment)
