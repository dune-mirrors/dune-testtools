"""
This module provides methods compare two ini files. They can be compared
exact, i.e. key-value-pair by key-value-pair. They can be fuzzy compared, i.e.
numbers are converted to floating point numbers and compared using absolute
and relative criterions. A zero threshold can be set for each key for to regard
a value under a threshold zero.

Keys can be excluded from comparison by specifying the key-list `exclude`.
"""

from __future__ import absolute_import
from dune.testtools.parametertree.dotdict import DotDict
from dune.testtools.parametertree.parser import parse_ini_file
from dune.testtools.escapes import extract_delimited


def floatify(x):
    try:
        return float(x)
    except ValueError:
        try:
            return float(extract_delimited(x, '"', '"'))
        except Exception:
            raise ValueError


def compare_ini(inifile1, inifile2,
                exclude=[],
                verbose=True):
    """
    Compare two ini files

    Required Arguments:

    :param inifile1: The filename of the first ini file
    :type inifile1:  string

    :param inifile2: The filename of the second ini file
    :type inifile2:  string

    Optional Arguments:

    :type exclude:  list
    :param exclude: A list of keys to be excluded from the comparison

    :type verbose:  bool
    :param verbose: If verbose output for test evaluation
    """
    # parse the ini files
    ini1 = parse_ini_file(inifile1)
    ini2 = parse_ini_file(inifile2)

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
        for key, value in ini1.items():
            # check if key exists in other dict
            if key not in ini2:
                print('Inifiles differ in key {}.'.format(key))
                print('Key {} not available in {}.'.format(key, inifile2))
                return 1

            # check if values are equal
            if value != ini2[key]:
                print('Inifiles differ in key {}. Values are {} and {}'.format(key, value, ini2[key]))
                print('Compared inifiles {} and {}.'.format(inifile1, inifile2))
                return 1
        # for ini2 just check the keys. note: this double checks most keys...
        for key in ini2:
            if key not in ini1:
                print('Key {} not available in {}.'.format(key, inifile1))
                return 1

    # if we came so far everything is fine
    return 0


def fuzzy_compare_ini(inifile1, inifile2,
                      absolute=1.5e-7, relative=1e-2,
                      zeroValueThreshold={}, exclude=[],
                      verbose=True):
    """
    Fuzzy compare two ini files

    Required Arguments:

    :param inifile1: The filename of the first ini file
    :type inifile1:  string

    :param inifile2: The filename of the second ini file
    :type inifile2:  string

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
    # parse the ini files
    ini1 = parse_ini_file(inifile1)
    ini2 = parse_ini_file(inifile2)

    # exclude keys
    for key in exclude:
        if key in ini1:
            del ini1[key]
        if key in ini2:
            del ini2[key]

    # iterate over the dicts
    for key, value in ini1.items():
        # check if key exists in other dict
        if key not in ini2:
            print('Inifiles differ in key {}.'.format(key))
            print('Key {} not available in {}.'.format(key, inifile2))
            return 1

        # check if the values can be converted to float
        try:
            value = floatify(value)
            ini2[key] = floatify(ini2[key])
        except ValueError:
            # do exact comparison, we can only do fuzzy float comparison
            if value != ini2[key]:
                print('Inifiles differ in key {}. Values are {} and {}'.format(key, value, ini2[key]))
                print('Compared inifiles {} and {}'.format(inifile1, inifile2))
                return 1
            else:
                continue

        # honour the zero threshold
        if key in zeroValueThreshold:
            if abs(value) < zeroValueThreshold[key] and abs(ini2[key] < zeroValueThreshold[key]):
                value = 0.0
                ini2[key] = 0.0

        # check if the values are equal
        diff = abs(value - ini2[key])

        # If the absolute criterion is satisfied we consider the numbers equal...
        # scale the absolute tolerance with the magnitude of the parameter
        if diff <= absolute * max(value, ini2[key]):
            continue

        largernumber = max(abs(value), abs(ini2[key]))
        # ...if not check the relative criterion
        if diff <= largernumber * relative:
            continue
        else:
            # the numbers are not equal
            if verbose:
                print('Difference is too large between: {} and {}'.format(value, ini2[key]))
                print('Compared inifiles {} and {}'.format(inifile1, inifile2))
            return 1

        # for ini2 just check the keys. note: this double checks most keys...
        for key in ini2:
            if key not in ini1:
                print('Key {} not available in {}.'.format(key, inifile1))
                return 1

    # if we came so far everything is fine
    return 0
