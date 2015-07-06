"""Test for the convergence test metaini python module"""
from __future__ import absolute_import
from ..convergencetest_metaini import *
from six.moves import range

def test_extract_convergence_test_info(dir):
    tests = extract_convergence_test_info(dir + "convtest.ini")
    # the meta ini file should yield 4 different convergence tests
    assert(len(tests) == 4)
    for configuration in tests:
        # each having a list of four different configurations (e.g. 4 refinements)
        assert(len(configuration) == 4)

def test_extract_convergence_test_info2(dir):
    tests = extract_convergence_test_info(dir + "convtest2.ini")
    # the meta ini file should yield 1 different convergence tests
    assert(len(tests) == 1)
    for configuration in tests:
        # each having a list of four different configurations (e.g. 2 refinements)
        assert(len(configuration) == 2)

def test_extract_convergence_test_info3(dir):
    tests = extract_convergence_test_info(dir + "convtest3.ini")
    # the meta ini file should yield 2 different convergence tests
    assert(len(tests) == 2)
    for configuration in tests:
        # each having a list of four different configurations (e.g. 2 refinements)
        assert(len(configuration) == 5)
        for c in configuration:
            assert(any(c["level"] in str(i) for i in range(0, 6)))

def test_extract_convergence_test_info4(dir):
    tests = extract_convergence_test_info(dir + "convtest4.ini")
    # the meta ini file should yield 2 different convergence tests
    assert(len(tests) == 2)
    for configuration in tests:
        # each having a list of four different configurations (e.g. 2 refinements)
        assert(len(configuration) == 5)
        for c in configuration:
            assert(any(c["level"] in i for i in ["a", "b", "c", "d", "e", "f"]))
