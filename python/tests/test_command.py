from __future__ import absolute_import
from dune_testtools.metaini import expand_meta_ini


def test_metaini(dir):
    c = expand_meta_ini(dir + "command.ini")
    assert("4" in [conf["ev"] for conf in c])
    assert(6 < float(c[0]["pi"]) < 7)
    assert(len(c) == 4)
