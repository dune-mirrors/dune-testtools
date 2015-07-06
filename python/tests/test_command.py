
from __future__ import absolute_import
from ..command import *
from ..parser import parse_ini_file
from ..metaini import expand_meta_ini

@meta_ini_command(name="some", argc=2)
def product(args=None):
    return str(int(args[0])*int(args[1]))

def test_basics():
    d = {}
    d["a"] = "CAPS | tolower"
    assert(command_registry().get("tolower", None))
    apply_generic_command(config=d, key="a")
    assert(d["a"] == "caps")

def test_parsed(dir):
    c = parse_ini_file(dir + "command.ini")
    for k in c:
        apply_generic_command(config=c, key=k)
    # simple operator
    assert(c["key"] == "bla")
    # double operator
    assert(c["other"] == "BLA")

def test_arguments():
    d = {}
    d["a"] = "bla | some 2 3"
    apply_generic_command(config=d, key="a")
    assert(d["a"] == "6")

def test_metaini(dir):
    c = expand_meta_ini(dir + "command.ini")
    assert("4" in [conf["ev"] for conf in c])
    assert(6 < float(c[0]["pi"]) < 7)
    assert(len(c) == 4)
