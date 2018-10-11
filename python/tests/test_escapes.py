from __future__ import absolute_import
from dune.testtools.escapes import *
from dune.testtools.metaini import *


def test_count():
    assert count_unescaped("{{\{", "{") == 2


def test_curly_bracket(dir):
    configs = expand_meta_ini(dir + "escape.mini")
    assert(len(configs) == 2)
