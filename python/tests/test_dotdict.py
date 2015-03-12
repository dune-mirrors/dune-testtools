from dotdict import DotDict

def test_dotdict():
    # define some arbitrary dotdict
    d = DotDict()
    d["a"] = "bla"
    d["b.c"] = "bla"
    d["b"]["d"] = "x"
    d["d.e.f"] = 1

    # do some comparisons
    assert(d["b.c"] == d["b"]["c"])
    assert(len(d) == 4)
    assert(d["a"] == d["b"]["c"])
    del d["d.e.f"]
    assert(len(d) == 3)

    # non-str key
    d[1] = 5

    # test the items method
    for k, v in d.items():
        assert(d[k] == v)

    # __contains__
    assert("b.c" in d)
    assert(not "d.e.f" in d)

    assert(str(d) == "{'a': 'bla', '1': 5, 'b': {'c': 'bla', 'd': 'x'}}")
