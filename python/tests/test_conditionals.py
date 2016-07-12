from dune.testtools.metaini import expand_meta_ini
from dune.testtools.conditionals import eval_boolean


def test_cond1(dir):
    c = expand_meta_ini(dir + "cond1.mini")
    assert(len(c) == 1)


def test_cond2(dir):
    config = expand_meta_ini(dir + "cond2.mini")
    res = {(1, 3): "BLA", (2, 3): "BLUBB", (2, 4): "BLUBB", (1, 4): "DEF"}
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
    assert(eval_boolean("x == x and x==x"))
    assert(eval_boolean("x == 'x' and 'x'==x"))
    assert(not eval_boolean("ax == x"))

    f = open(dir + "tmp.mini", 'w')
    f.write("a = 2, 3 | expand \n {a} == 2 | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("b = 2, 3 | expand \n {b} > 2 | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("c = 2, 3 | expand \n 2 < {c} | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("d = 2, 3 | expand \n \"2 == {d}\" | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("e = 2.55, 12.55 | expand \n {e} < 10 | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("f = bla, blubb | expand \n {f} == bla | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("g = bla, blubb | expand \n {g} == 'bla' | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("h = bla, blubb | expand \n '{h}' == 'bla' | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)

    f = open(dir + "tmp.mini", 'w')
    f.write("i = bla, blubb | expand \n '{i}' == bla | exclude")
    f.close()
    assert(len(expand_meta_ini(dir + "tmp.mini")) == 1)


def test_double_command(dir):
    f = open(dir + "tmp.mini", 'w')
    f.write("bla = bla, blubb | toupper | expand deg \n\
             degree = 1, 2 | expand deg")
    f.close()
    result = expand_meta_ini(dir + "tmp.mini")
    assert(len(result) == 2)
    assert(result[0]["bla"] == 'BLA')
    assert(result[1]["bla"] == 'BLUBB')
