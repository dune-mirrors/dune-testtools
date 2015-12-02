from dune.testtools.metaini import expand_meta_ini
from dune.testtools.static_metaini import *


def test_has_correct_static_info(dir):
    configs = expand_meta_ini(dir + "discard.mini")
    for c in configs:
        assert len(c['__cmake_guards']) == 1

    static = extract_static_info(dir + "discard.mini", add_guards=True)

    for conf in static['__CONFIGS']:
        assert len(static[conf]['__GUARDS']) == 1
