"""
.. module:: compareini
    :synopsis: A module for comparing two ini files.

This module provides methods compare two ini files. They can be compared
exact, i.e. key-value-pair by key-value-pair. They can be fuzzy compared, i.e.
numbers are converted to floating point numbers and compared using absolute
and relative criterions. A zero threshold can be set for each key for to regard
a value under a threshold zero.

Keys can be excluded from comparison by specifying the key-list `exclude`.
"""

from __future__ import absolute_import
from dune.common.ini.dotdict import DotDict
from dune.common.ini.parser import parse_ini_file

def compare_ini(ini1, ini2, exclude=[], verbose=True):
    """
    Compare two ini files

    Required Arguments:

    :param ini1: The filename of the first ini file
    :type ini1:  string

    :param ini2: The filename of the second ini file
    :type ini2:  string

    Optional Arguments:

    :type exclude:  list
    :param exclude: A list of keys to be excluded from the comparison

    :type verbose:  bool
    :param verbose: If verbose output for test evaluation
    """
    # parse the ini files
    ini1 = parse_ini_file(ini1)
    ini2 = parse_ini_file(ini2)

    # exclude keys
    for key in exclude:
        if key in ini1:
            del ini1[key]
        if key in ini2:
            del ini2[key]

    # compare dicts
    if not verbose:
        if ini1 == ini2:
            return 0
        else:
            return 1
    else:
        # TODO verbose comparison
        if ini1 == ini2:
            return 0
        else:
            return 1


def fuzzy_compare_ini(ini1, ini2, absolute=1.5e-7, relative=1e-2, zeroValueThreshold={}, exclude=[], verbose=True):
    """
    Fuzzy compare two ini files

    Required Arguments:

    :param ini1: The filename of the first ini file
    :type ini1:  string

    :param ini2: The filename of the second ini file
    :type ini2:  string

    Optional Arguments:

    :type absolute:  float
    :param absolute: The epsilon used for comparing numbers with an absolute criterion

    :type relative:  float
    :param relative: The epsilon used for comparing numbers with an relative criterion

    :type zeroValueThreshold:  dict
    :param zeroValueThreshold: A dictionary of parameter value pairs that set the threshold under
                               which a number is treated as zero for a certain parameter. Use this parameter if
                               you have to avoid comparisons of very small numbers for a certain parameter.

    :type exclude:  list
    :param exclude: A list of keys to be excluded from the comparison

    :type verbose:  bool
    :param verbose: If verbose output for test evaluation
    """
    # TODO
    return 0
