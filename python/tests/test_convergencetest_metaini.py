"""Test for the convergence test metaini python module"""
# from convergencetest_metaini import *
#
# def test_extract_convergence_test_info():
#     tests = extract_convergence_test_info("./tests/convtest.ini")
#     # the meta ini file should yield 4 different convergence tests
#     assert(len(tests) == 4)
#     for configuration in tests:
#         # each having a list of four different configurations (e.g. 4 refinements)
#         assert(len(configuration) == 4)
#
# def test_extract_convergence_test_info2():
#     tests = extract_convergence_test_info("./tests/convtest2.ini")
#     # the meta ini file should yield 1 different convergence tests
#     assert(len(tests) == 1)
#     for configuration in tests:
#         # each having a list of four different configurations (e.g. 2 refinements)
#         assert(len(configuration) == 2)
#
# def test_extract_convergence_test_info3():
#     tests = extract_convergence_test_info("./tests/convtest3.ini")
#     # the meta ini file should yield 2 different convergence tests
#     assert(len(tests) == 2)
#     for configuration in tests:
#         # each having a list of four different configurations (e.g. 2 refinements)
#         assert(len(configuration) == 5)
#         for c in configuration:
#             assert(any(c["level"] in str(i) for i in range(0, 6)))
#
# def test_extract_convergence_test_info4():
#     tests = extract_convergence_test_info("./tests/convtest4.ini")
#     # the meta ini file should yield 2 different convergence tests
#     assert(len(tests) == 2)
#     for configuration in tests:
#         # each having a list of four different configurations (e.g. 2 refinements)
#         assert(len(configuration) == 5)
#         for c in configuration:
#             assert(any(c["level"] in i for i in ["a", "b", "c", "d", "e", "f"]))
