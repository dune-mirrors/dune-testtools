""" A module defining a dictionary, that allows ot access nested structures by having dots in keys

d["a"]["b"] ==  d["a.b"]
"""
from __future__ import absolute_import


class DotDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        key = str(key)
        if "." in key:
            group, key = key.split(".", 1)
            return dict.__getitem__(self, group)[key]
        else:
            return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        key = str(key)
        if "." in key:
            group, key = key.split(".", 1)
            if group not in self:
                dict.__setitem__(self, group, DotDict())
            dict.__getitem__(self, group).__setitem__(key, value)
        else:
            dict.__setitem__(self, key, value)

    def __contains__(self, key):
        key = str(key)
        if "." in key:
            group, key = key.split(".", 1)
            if group not in self:
                return False
            return dict.__getitem__(self, group).__contains__(key)
        else:
            return dict.__contains__(self, key)

    def __delitem__(self, key):
        key = str(key)
        if "." in key:
            group, key = key.split(".", 1)
            dict.__getitem__(self, group).__delitem__(key)
            if len(dict.__getitem__(self, group)) is 0:
                dict.__delitem__(self, group)
        else:
            dict.__delitem__(self, key)

    def __len__(self):
        return sum([1 for i in self])

    def __iter__(self, prefix=[]):
        for i in dict.__iter__(self):
            if type(self[i]) is DotDict:
                prefix.append(i)
                for x in self[i].__iter__(prefix):
                    yield x
                prefix.pop()
            else:
                def groupname():
                    result = ""
                    for p in prefix:
                        result = result + p + "."
                    return result
                yield groupname() + i

    def __str__(self):
        s = ""
        for k, v in list(self.items()):
            s = s + "'" + str(k) + "': '" + str(v) + "', "
        return "{" + s[:-2] + "}"

    def filter(self, filterList):
        d = DotDict()
        for k in self:
            if True in [k.startswith(f) for f in filterList]:
                d[k] = self[k]
        return d

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def __eq__(self, other):
        return tuple(sorted(self.items())) == tuple(sorted(other.items()))

    def __lt__(self, other):
        """ make the DotDict orderable to enforce an order on a list of ini files
        This is only well-defined for dicts sharing the set of keys.
        """
        if tuple(sorted(self.keys())) != tuple(sorted(other.keys())):
            return tuple(sorted(self.keys())) < tuple(sorted(other.keys()))
        for k in sorted(self.keys()):
            if self[k] < other[k]:
                return True
            if self[k] > other[k]:
                return False

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        return [(k, self[k]) for k in self]

    def keys(self):
        return [k for k in self]

    def values(self):
        return [self[k] for k in self]
