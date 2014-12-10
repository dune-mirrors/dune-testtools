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

def exists_unescaped(str, char):
    if len(str) is 0:
        return False
    if str[0] is char:
        return True
    for i in range(1, len(str)):
        if (str[i] is char) and (str[i - 1] != "\\"):
            return True
    return False

def strip_escapes(str, char):
    return  str.replace("\\" + char, char)

def escaped_split(str, delimiter=" ", maxsplit=-1):
    # perform an ordinary split without taking into account escaping
    normal = str.split(delimiter, maxsplit)

    # define the resulting list
    result = []

    # define a prefix from previous items
    concat = ""
    for item in normal:
        # check whether the delimiter after this item was escaped
        if item.endswith("\\"):
            print "item[:-1] : {}".format(item[:-1])
            concat = concat + item[:-1] + delimiter
        else:
            result.append(concat + item)
            concat = ""

    if not concat is "":
        result.append(concat)

    print "returning {}".format(result)
    return result
