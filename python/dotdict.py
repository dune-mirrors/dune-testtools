""" A module defining a dictionary, that allows ot access nested structures by having dots in keys

d["a"]["b"] ==  d["a.b"]
"""

from escapes import exists_unescaped, escaped_split

class DotDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
            return dict.__getitem__(self, group)[key]
        else:
            return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
            if not group in self:
                dict.__setitem__(self, group, DotDict())
            dict.__getitem__(self, group).__setitem__(key, value)
        else:
            dict.__setitem__(self, key, value)

    def __contains__(self, key):
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
            if not group in self:
                return False
            return dict.__getitem__(self, group).__contains__(key)
        else:
            return dict.__contains__(self, key)
