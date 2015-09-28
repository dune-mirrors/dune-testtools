from __future__ import absolute_import
from dune.testtools.parser import parse_ini_file
from dune.testtools.escapes import count_unescaped


def test_parse1(dir):
    # A 'normal' ini file that uses all subgrouping mechanisms
    parsed = parse_ini_file(dir + "parse1.ini")
    assert(len(parsed) == 8)
    assert(parsed['x'] == '5')
    assert(parsed['y'] == 'str')
    assert(parsed['group.y'] == 'str')
    assert(parsed['group.x'] == '5')
    assert(parsed['group.z'] == '1')
    assert(parsed['group.subgroup.y'] == 'str')
    assert(parsed['group.subgroup.z'] == '1')


def test_parse2(dir):
    # A file that contains non-key-value data
    parsed = parse_ini_file(dir + "parse2.ini")['__local.conditionals']
    assert(len(parsed) == 2)
    assert(parsed['0'] == '{x} == {y}')
    assert(parsed['1'] == '{x} == {y}')


def test_parse3(dir):
    # Testing all sorts of escapes
    parsed = parse_ini_file(dir + "parse3.ini")
    assert(count_unescaped(parsed['a'], '|') == 0)
    assert(count_unescaped(parsed['c'], ',') == 3)
    assert(count_unescaped(parsed['d'], '"') == 2)
