from __future__ import absolute_import
from dune.testtools.metaini import expand_meta_ini


def test_metaini(dir):
    c = expand_meta_ini(dir + "command.ini")
    assert("4" in [conf["ev"] for conf in c])
    assert(6 < float(c[0]["pi"]) < 7)
    assert(len(c) == 4)


def test_complex_command_deps(dir):
    c = expand_meta_ini(dir + "complexcommand.mini")
    assert(len(c) == 2)
    assert("2" in [conf["b"] for conf in c])
    assert("5" in [conf["b"] for conf in c])


def test_repeat_command(dir):
    c = expand_meta_ini(dir + "repeat.mini")
    assert(len(c) == 2)
    for conf in c:
        assert(len(conf["cells"].split()) == int(conf["dim"]))
