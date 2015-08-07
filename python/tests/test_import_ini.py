from __future__ import absolute_import
from dune.testtools.metaini import expand_meta_ini


def test_import(dir):
    configs = expand_meta_ini(dir + "import.ini")
    assert(configs[0]["a"] == "TEST")
    assert(len(configs) == 36)
