from parser import parse_ini_file
from escapes import count_unescaped

def test_parse1():
    # A 'normal' ini file that uses all subgrouping mechanisms
    parsed = parse_ini_file("./tests/parse1.ini")
    assert(len(parsed) == 8)
    assert(parsed['x'] == '5')
    assert(parsed['y'] == 'str')
    assert(parsed['group.y'] == 'str')
    assert(parsed['group.x'] == '5')
    assert(parsed['group.z'] == '1')
    assert(parsed['group.subgroup.y'] == 'str')
    assert(parsed['group.subgroup.z'] == '1')

def test_parse2():
    # A file that contains non-key-value data
    parsed = parse_ini_file("./tests/parse2.ini")['__local.conditionals']
    assert(len(parsed) == 3)
    assert(parsed['0'] == 'blub')
    assert(parsed['1'] == '{x} == {y} | doSomething')
    assert(parsed['2'] == '{x} == {y} | doSomething')

def test_parse3():
    # Testing all sorts of escapes
    parsed = parse_ini_file("./tests/parse3.ini")
    assert(count_unescaped(parsed['a'], '|') == 1)
    assert(count_unescaped(parsed['b'], '|') == 1)
    assert(count_unescaped(parsed['c'], ',') == 3)
    assert(count_unescaped(parsed['d'], '"') == 2)
