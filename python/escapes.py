""" A module for handling escaped characters in the INI project

We have a lot of special characters in our project: Assignment,
comment, key-dependent value syntax, list separators etc.
This file provides some methods to implement escaping these
characters.

TODO:
- A backslash cannot be escaped at the moment: I am not willing to spend
  another afternoon in escape hell.
"""

import re

def count_unescaped(str, char):
    return len(re.findall("(?<!\\\\){}".format(re.escape(char)), str))

def exists_unescaped(str, char):
    return count_unescaped(str, char) != 0

def strip_escapes(str, char):
    return str.replace("\\" + char, char)

def escaped_split(str, delimiter=" ", maxsplit=0):
    return [i.replace("\\{}".format(delimiter), delimiter).strip() for i in re.split("(?<!\\\\){}".format(re.escape(delimiter)), str, maxsplit)]

def lookup_and_modify_key(d, af):
    def _lookup_and_modify_key(matchobj):
        return af(d, matchobj.group(0)[1:-1])
    return _lookup_and_modify_key

def replace_delimited(s, d, leftdelimiter="{", rightdelimiter="}", access_func=lambda d,k: d[k]):
    return re.sub("{0}[^{0}{1}]+{1}".format(leftdelimiter, rightdelimiter), lookup_and_modify_key(d, access_func), s, count=1)