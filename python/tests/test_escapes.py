from __future__ import absolute_import
from dune_testtools.escapes import *


def test_count():
    assert count_unescaped("{{\{", "{") == 2
