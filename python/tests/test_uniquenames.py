from metaini import expand_meta_ini

def check_uniqueness(_list, key):
    found = []
    for l in _list:
        if l[key] in l:
            return False
        else:
            found.append(l[key])
    return True

def test_metaini1():
    configs = expand_meta_ini("./tests/metaini1.mini")
    assert(check_uniqueness(configs, "__name"))

def test_metaini2():
    configs = expand_meta_ini("./tests/metaini2.mini")
    assert(check_uniqueness(configs, "__name"))

def expect_exception(excepttype, f, *args):
    try:
        f(*args)
    except excepttype:
        return True
    return False

def test_exception_on_depending_on_unique_key():
    assert(expect_exception(ValueError, expand_meta_ini, "./tests/wrongunique.ini"))