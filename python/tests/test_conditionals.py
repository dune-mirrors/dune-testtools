from dune_testtools.metaini import expand_meta_ini
from dune_testtools.conditionals import eval_boolean

def test_cond1(dir):
    c = expand_meta_ini(dir + "cond1.mini")
    assert(len(c) == 1)

def test_cond2(dir):
    config = expand_meta_ini(dir + "cond2.mini")
    res = {(1,3): "BLA", (2,3): "BLUBB", (2,4): "BLUBB", (1,4): "DEF"}
    for c in config:
        if c["x"] is "1":
            assert(c["__LABELS.PRIORITY"] == "NIGHTLY")
        else:
            assert("__LABELS.PRIORITY" not in c)
        assert(c["__LABELS.CUSTOM"] == res[(int(c["x"]), int(c["y"]))])

def test_quoting_magic(dir):
    assert(eval_boolean("x == x"))
    assert(eval_boolean("'x' == x"))
    assert(eval_boolean("x == 'x'"))
    assert(eval_boolean("'x' == 'x'"))
    assert(not eval_boolean("ax == x"))
    assert(len(expand_meta_ini(dir + "cond3.mini", whiteFilter=["a"])) == 1)
    assert(len(expand_meta_ini(dir + "cond3.mini", whiteFilter=["b"])) == 1)
    assert(len(expand_meta_ini(dir + "cond3.mini", whiteFilter=["c"])) == 1)
    assert(len(expand_meta_ini(dir + "cond3.mini", whiteFilter=["d"])) == 1)
    assert(len(expand_meta_ini(dir + "cond3.mini", whiteFilter=["e"])) == 1)
