from escapes import *

def test_count():
    assert count_unescaped("{{\{", "{") == 2