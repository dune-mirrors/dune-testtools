"""Test for the convergence test metaini python module"""
from convergencetest_metaini import *

def test_extract_convergence_test_info():
    tests = extract_convergence_test_info("./tests/convtest.ini")
    # the meta ini file should yield 4 different convergence tests
    assert(len(tests) == 4)
    for configuration in tests:
        # each having a list of four different configurations (e.g. 4 refinements)
        assert(len(configuration) == 4)

def test_extract_convergence_test_info2():
    tests = extract_convergence_test_info("./tests/convtest2.ini")
    # the meta ini file should yield 1 different convergence tests
    assert(len(tests) == 1)
    for configuration in tests:
        # each having a list of four different configurations (e.g. 2 refinements)
        assert(len(configuration) == 2)

def test_extract_convergence_test_info3():
    tests = extract_convergence_test_info("./tests/convtest3.ini")
    print str(tests)
    # the meta ini file should yield 2 different convergence tests
    assert(len(tests) == 2)
    for configuration in tests:
        print str(len(configuration)) + "\n"
        # each having a list of four different configurations (e.g. 2 refinements)
        assert(len(configuration) == 5)
