from __future__ import absolute_import
from dune.testtools.wrapper.compareini import *


def test_inicompare_fuzzy(dir):
    f = open(dir + "tmp.out", 'w')
    f.write("a = 2\nb = 3.0\nc = bla")
    f.close()

    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp.out") == 0)

    f = open(dir + "tmp2.out", 'w')
    f.write("a = 2\nb = 4.0\nc = bla")
    f.close()

    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp2.out") == 1)
    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp2.out", exclude=['b']) == 0)


def test_inicompare_exact(dir):
    f = open(dir + "tmp.out", 'w')
    f.write("a = 2\nb = 3.0\nc = bla")
    f.close()

    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp.out") == 0)

    f = open(dir + "tmp2.out", 'w')
    f.write("a = 2\nb = 3.00001\nc = bla")
    f.close()

    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp2.out") == 0)

    f = open(dir + "tmp.out", 'w')
    f.write("a = 2\nb = 1e-15\nc = bla")
    f.close()
    f = open(dir + "tmp2.out", 'w')
    f.write("a = 2\nb = 2e-15\nc = bla")
    f.close()

    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp2.out") == 1)
    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp2.out", exclude=['b']) == 0)
    assert(fuzzy_compare_ini(dir + "tmp.out", dir + "tmp2.out", zeroValueThreshold={'b': 1e-14}) == 0)
