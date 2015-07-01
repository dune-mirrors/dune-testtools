from __future__ import absolute_import
from ..metaini import expand_meta_ini

def test_import():
    configs = expand_meta_ini("./tests/import.ini")
    assert(configs[0]["a"] == "TEST")
    assert(len(configs) == 36)