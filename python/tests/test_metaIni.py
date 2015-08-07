from __future__ import absolute_import
from dune.testtools.metaini import *


def test_metaini1(dir):
    configs = expand_meta_ini(dir + "metaini1.mini")
    assert(len(configs) == 72)

    configs = expand_meta_ini(dir + "metaini1.mini", whiteFilter=("g",))
    assert(len(configs) == 12)

    configs = expand_meta_ini(dir + "metaini1.mini", whiteFilter=("g", "a"))
    assert(len(configs) == 24)

    configs = expand_meta_ini(dir + "metaini1.mini", whiteFilter=("a",))
    assert(len(configs) == 2)

    configs = expand_meta_ini(dir + "metaini1.mini", whiteFilter=("garbagekey",), addNameKey=False)
    assert(str(configs) == '[{}]')

    configs = expand_meta_ini(dir + "metaini1.mini", blackFilter=["a"])
    assert(len(configs) == 36)


def test_metaini2(dir):
    configs = expand_meta_ini(dir + "metaini2.mini")
    assert(len(configs) == 24)
