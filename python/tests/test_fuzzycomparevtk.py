""" A test for the vtu fuzzy compare"""
from __future__ import absolute_import

from ..fuzzy_compare_vtk import compare_vtk

def test_0():
    assert(compare_vtk("./tests/vtu1.vtu", "./tests/vtu2.vtu") == 0)
def test_1():
    assert(compare_vtk("./tests/vtu1.vtu", "./tests/vtu21.vtu") == 1)
def test_2():
    assert(compare_vtk("./tests/vtu1.vtu", "./tests/vtu3.vtu") == 0)
def test_3():
    assert(compare_vtk("./tests/vtu1.vtu", "./tests/vtu31.vtu") == 1)
