from dune_testtools.metaini import expand_meta_ini

def test_cond1(dir):
    c = expand_meta_ini(dir + "cond1.mini")
    assert(len(c) == 1)

def test_cond2(dir):
    config = expand_meta_ini(dir + "cond2.mini")
    res = {(1,3): "BLA", (2,3): "BLUBB", (2,4): "BLUBB", (1,4): "DEF"}
    for c in config:
        if c["x"] is "1":
            assert(c["__STATIC.LABELS.PRIORITY"] == "NIGHTLY")
        else:
            assert("__STATIC.LABELS.PRIORITY" not in c)
        assert(c["__STATIC.LABELS.CUSTOM"] == res[(int(c["x"]), int(c["y"]))])