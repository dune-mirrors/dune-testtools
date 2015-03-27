import command
from parseIni import parse_ini_file

def test_basics():
    assert(command._registry.get("tolower", None))
    assert(command._registry["tolower"](value="CAPS") == "caps")
    assert(command._registry["tolower"](value="CAPS", shit=0) == "caps")

def test_parsed():
    c = parse_ini_file("./tests/command.ini")
    for k in c:
        c[k] = command.apply_generic_command(k, c[k])
    # simple operator
    assert(c["key"] == "bla")
    # double operator
    assert(c["other"] == "BLA")
