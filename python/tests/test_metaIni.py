from metaIni import *

def test_metaini1():
    configs = expand_meta_ini("./tests/metaini1.mini")
    assert(len(configs) == 72)

    configs = expand_meta_ini("./tests/metaini1.mini", filterKeys=("g",))
    assert(len(configs) == 12)
    
    configs = expand_meta_ini("./tests/metaini1.mini", filterKeys=("g", "a"))
    assert(len(configs) == 24)

    configs = expand_meta_ini("./tests/metaini1.mini", filterKeys=("a",))
    assert(len(configs) == 2)

    configs = expand_meta_ini("./tests/metaini1.mini", filterKeys=("garbagekey",), addNameKey=False)
    assert(str(configs) == '[{}]')


def test_metaini2():
    configs = expand_meta_ini("./tests/metaini2.mini")
    assert(len(configs) == 24)