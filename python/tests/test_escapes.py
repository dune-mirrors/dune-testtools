from __future__ import absolute_import
from dune.testtools.escapes import *


def test_count():
    assert count_unescaped("{{\{", "{") == 2
