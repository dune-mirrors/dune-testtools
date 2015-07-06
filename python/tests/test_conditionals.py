from ..metaini import expand_meta_ini

def test_cond1(dir):
    c = expand_meta_ini(dir + "cond1.mini")
    assert(len(c) == 1)