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


def test_range_command(dir):
    c = expand_meta_ini(dir + "range.mini")
    assert(len(c) == 7)
    vals = set("i{}".format(i) for i in range(7))
    for conf in c:
        assert(conf["val"] in vals)
        vals.discard(conf["val"])

    vals2 = set("i{}".format(2 * i + 1) for i in range(7))
    for conf in c:
        assert(conf["val2"] in vals2)
        vals.discard(conf["val2"])


def test_zfill_command(dir):
    c = expand_meta_ini(dir + "zfill.mini")
    assert(len(c) == 10)
    vals = set(str(i).zfill(4) for i in range(10))
    for conf in c:
        assert(conf["number_str"] in vals)
        vals.discard(conf["number_str"])
