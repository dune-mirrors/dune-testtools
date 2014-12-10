""" A module for handling escaped characters in the INI project

We have a lot of special characters in our project: Assignment,
comment, key-dependant value syntax, list separators etc.
This file provides some methods to implement escaping these
characters. It seems like at some point a decision on whether
rewriting everything using regular expression is necessary.

TODO:
- A backslash cannot be escaped at the moment: I am not willing to spend
  an afternoon in escape hell.
"""

import re

def count_unescaped(str, char):
    return len(re.findall("{}(?!{})".format(re.escape(char),"\\\\"), str))

def exists_unescaped(str, char):
    return count_unescaped(str, char) != 0

def strip_escapes(str, char):
    return str.replace("\\" + char, char)

def escaped_split(str, delimiter=" ", maxsplit=-1):
    # perform an ordinary split without taking into account escaping
    if (len(delimiter) is 1):
        normal = str.split(delimiter, maxsplit)
    else:
        # the re split was needed here, it might crash with characters that need escaping themself
        # within the delimiter...
        import re
        normal = re.split(delimiter, str)

    # define the resulting list
    result = []

    # define a prefix from previous items
    concat = ""
    for item in normal:
        # check whether the delimiter after this item was escaped
        if item.endswith("\\"):
            concat = concat + item[:-1] + delimiter
        else:
            result.append(concat + item)
            concat = ""

    if not concat is "":
        result.append(concat)

    return result
