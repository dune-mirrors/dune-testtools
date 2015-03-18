from static_metaini import *

def test_empty_static():
    static = extract_static_info("./tests/metaini1.mini")
    # reading static information from a file without such should result in exactly one configuration.
    assert(len(static['__CONFIGS']) == 1)

# TODO fails, but shouldnt
# def test_static1():
#     static = extract_static_info("./tests/static1.mini")
#     assert(static == None)
    