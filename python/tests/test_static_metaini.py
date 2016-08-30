from __future__ import absolute_import
from dune.testtools.static_metaini import *


def test_empty_static(dir):
    static = extract_static_info(dir + "metaini1.mini")
    # reading static information from a file without such should result in exactly one configuration.
    assert(len(static['__CONFIGS']) == 1)


def test_static1(dir):
    static = extract_static_info(dir + "static1.mini")

    static_check = {'G1_0000': {'COMPILE_DEFINITIONS': {'GRID': 'G1', 'SOLVER': 'Solver1a'}}, 'G1_0001': {'COMPILE_DEFINITIONS': {'GRID': 'G1', 'SOLVER': 'Solver1b'}}, 'G2_0001': {'COMPILE_DEFINITIONS': {'GRID': 'G2', 'SOLVER': 'Solver1a'}}, 'G2_0000': {'COMPILE_DEFINITIONS': {'GRID': 'G2', 'SOLVER': 'Solver1b'}}, 'G3': {'COMPILE_DEFINITIONS': {'GRID': 'G3', 'SOLVER': 'Solver2'}}, '__CONFIGS': ['G1_0000', 'G2_0000', 'G2_0001', 'G1_0001', 'G3'], '__STATIC_DATA': ['GRID', 'SOLVER']}
    unmatched_item = set(static) ^ set(static_check)
    assert(len(unmatched_item) == 0)
