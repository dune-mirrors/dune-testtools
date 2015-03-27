import command

def test_basics():
    assert(command._registry.get("tolower", None))
    assert(command._registry["tolower"](value="CAPS") == "caps")
    assert(command._registry["tolower"](value="CAPS", shit=0) == "caps")