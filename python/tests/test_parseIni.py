from parseIni import *

def test_parse1():
    # A 'normal' ini file that is parsed with and without subgroups and as strings or as converted values
    parsed = parse_ini_file("./tests/parse1.ini")
    real = {'x': 5, 'y': 'str', 'group': {'y': 'str', 'x': 5, 'z': 1, 'subgroup': {'y': 'str', 'x': 5, 'z': 1}}}
    assert(parsed == real)

    parsed = parse_ini_file("./tests/parse1.ini", asStrings=True)
    real = {'y': 'str', 'x': '5', 'group': {'y': 'str', 'x': '5', 'z': '1', 'subgroup': {'y': 'str', 'x': '5', 'z': '1'}}}
    assert(parsed == real)

def test_parse2():
    # An ini file that contains such screwed up comments that it is actually empty
    parsed = parse_ini_file("./tests/parse2.ini", commentChar=('&', '$'))
    assert(parsed == {})

def test_parse3():
    # A multicharacter assignment operator, that is used without caring about spaces before/after at all
    parsed = parse_ini_file("./tests/parse3.ini", assignment="complex")
    real = {'y': 'str', 'x': 5, 'group': {'x': 5, 'z': 1, 'subgroup': {'z': 1}}}
    assert(parsed == real)

