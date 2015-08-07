from __future__ import absolute_import
from dune.testtools.metaini import expand_meta_ini


def check_uniqueness(_list, key):
    found = []
    for l in _list:
        if l[key] in l:
            return False
        else:
            found.append(l[key])
    return True


def test_metaini1(dir):
    configs = expand_meta_ini(dir + "metaini1.mini")
    assert(check_uniqueness(configs, "__name"))


def test_metaini2(dir):
    configs = expand_meta_ini(dir + "metaini2.mini")
    assert(check_uniqueness(configs, "__name"))


def expect_exception(excepttype, f, *args):
    try:
        f(*args)
    except excepttype:
        return True
    return False


def test_exception_on_depending_on_unique_key(dir):
    assert(expect_exception(ValueError, expand_meta_ini, dir + "wrongunique.ini"))


def test_total_order_on_configs(dir):
    configs = expand_meta_ini(dir + "metaini1.mini", addNameKey=True)
    for i in range(len(configs) - 1):
        assert(configs[i] < configs[i + 1])
