""" A module defining a dictionary, that allows ot access nested structures by having dots in keys

d["a"]["b"] ==  d["a.b"]
"""

from escapes import exists_unescaped, escaped_split

class DotDict(dict):
    def __init__(self, from_str=None, *args, **kwargs):
         if from_str:
             import ast
             for k, v in ast.literal_eval(from_str).items():
                 self.__setitem__(k, v)
         else:
             dict.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        key = str(key)
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
            return dict.__getitem__(self, group)[key]
        else:
            return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        key = str(key)
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
            if not group in self:
                dict.__setitem__(self, group, DotDict())
            dict.__getitem__(self, group).__setitem__(key, value)
        else:
            dict.__setitem__(self, key, value)

    def __contains__(self, key):
        key = str(key)
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
            if not group in self:
                return False
            return dict.__getitem__(self, group).__contains__(key)
        else:
            return dict.__contains__(self, key)

    def __delitem__(self, key):
        key = str(key)
        if exists_unescaped(key, "."):
            group, key = escaped_split(key, ".", maxsplit=1)
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
        for k, v in self.items():
            s = s + "'" + str(k) + "': '" + str(v) + "', "
        return "{" + s[:-2] + "}"


    def items(self):
        return [(k, self[k]) for k in self]
