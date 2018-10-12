"""A module for handling escaped characters in in ini files

.. currentmodule:: dune.testtools.escapes

We have a lot of special characters in our project: assignment,
comment, key-dependent value syntax, list separators, etc.
This file provides some methods to escape these characters.

.. note::
    Backslashes cannot be escaped at the moment.

"""
from __future__ import absolute_import
import re


def count_unescaped(str, char):
    """Counts the number of unescaped characters `char` in the string `str`.

       :param str: The string to find the unescaped characters in
       :type str:  string
       :param char: A single character of interest
       :type char:  string
       :returns: Amount of unescaped `char` that exist in `str`
       :rtype: int
    """
    if len(char) > 1:
        raise ValueError('Only a single character can be counted.')
    return len(re.findall("(?<!\\\\){}".format(re.escape(char)), str))


def exists_unescaped(str, char):
    """Checks if a character `char` exists unescaped in the string `str`.

       :param str: The string to find the unescaped characters in
       :type str:  string
       :param char: A single character of interest
       :type char:  string
       :returns: If `char` exists in `str`
       :rtype: bool
    """
    return count_unescaped(str, char) != 0


def strip_escapes(str, char):
    """Strips the escaping backslash off all appearances of `char` in the string `str`.

       :param str: The string to find the unescaped characters in
       :type str:  string
       :param char: A single character of interest
       :type char:  string
       :returns: The modified string
       :rtype: string
    """
    if len(char) > 1:
        raise ValueError('Please provide a single character.')
    return str.replace("\\" + char, char)


def escaped_split(str, delimiter=" ", maxsplit=0):
    """Split a string `str` at each occurence of the delimiter.

       :param str: The string to find the unescaped characters in
       :type str:  string
       :param delimiter: A delimiter at which splitting is performed
       :type delimiter:  string
       :param maxsplit: On how many delimiters the action gets applied
       :type maxsplit:  int
       :returns: The modified string
       :rtype: string

       For `maxsplit` = 0 (default) we split at every delimiter, for `maxsplit` = n until
       the n'th occurence of the delimiter.
    """
    return [i.replace("\\{}".format(delimiter), delimiter).strip() for i in re.split("(?<!\\\\){}".format(re.escape(delimiter)), str, maxsplit)]


def lookup_and_modify_key(d, af):
    """Helper function returning a function object for :func:`replace_delimited`

        .. todo::
            Is this of general use or can it be put inside :func:`replace_delimited`?
    """
    def _lookup_and_modify_key(matchobj):
        return af(d, matchobj.group(0)[1:-1])
    return _lookup_and_modify_key


def replace_delimited(str, d, leftdelimiter="{", rightdelimiter="}", access_func=lambda d, k: d[k]):
    """Replace a delimited string (inside a string `s`) with a replacement rule
       provided by a key-value pair in the dictionary `d`. The delimted string is the key of the
       dictionary while the value is the replacement. More general the dictionary can be
       any container containing the replacement rule that can be accessed through the access
       function `access_func` (default standard dict key-value access).

       :param str: The string to be modified
       :type str: string
       :param d: The replacement rule(s)
       :type d: dict
       :param leftdelimiter: The left delimiter character
       :type leftdelimiter: string
       :param rightdelimiter: The right delimiter character
       :type rightdelimiter: string
       :param access_func: The access function for `d`
       :type access_func: function

       :returns: The modified string
       :rtype: string

       Application:

       For resolution of the bracket operator in meta ini files, we have a dictionary with values that
       possbily depend on other key's values that possbily depend on other key's values again.
       This function can resolve one level of dependency for a single key-value pair using the other
       key-value pairs in the dictionary as replacement rule.
    """
    return re.sub("(?<!\\\\){0}[^{0}{1}]+(?<!\\\\){1}".format(leftdelimiter, rightdelimiter), lookup_and_modify_key(d, access_func), str, count=1)


def extract_delimited(str, leftdelimiter="[", rightdelimiter="]"):
    """Extract the first found string between two delimiters.

       :param str: The string to extract from
       :type str: string
       :param leftdelimiter: The left delimiter character
       :type leftdelimiter: string
       :param rightdelimiter: The right delimiter character
       :type rightdelimiter: string

       :returns: The first string that was found between the delimiters
       :rtype: string
    """
    return escaped_split(escaped_split(str, delimiter=leftdelimiter, maxsplit=1)[1], delimiter=rightdelimiter, maxsplit=1)[0]


def exists_delimited(str, value, leftdelimiter="{", rightdelimiter="}"):
    """Check if a string `value` exists between two delimiters inside a string `str`.

       :param str: The string to parse
       :type str: string
       :param value: The string to find between the delimiters
       :type value: string
       :param leftdelimiter: The left delimiter character
       :type leftdelimiter: string
       :param rightdelimiter: The right delimiter character
       :type rightdelimiter: string

       :returns: If `value` was found between delimiters
       :rtype: bool
    """
    return exists_unescaped(str, leftdelimiter + value + rightdelimiter)
