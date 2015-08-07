""" A test for the vtu fuzzy compare"""
from __future__ import absolute_import
from dune_testtools.wrapper.fuzzy_compare_vtk import compare_vtk


def test_failing_comparison(dir):
    assert(compare_vtk(dir + "vtu.vtu", dir + "vtu1.vtu") == 1)


def test_different_parameter_order(dir):
    assert(compare_vtk(dir + "vtu.vtu", dir + "vtu2.vtu") == 0)


def test_different_grid_order(dir):
    assert(compare_vtk(dir + "vtu.vtu", dir + "vtu3.vtu") == 0)


def test_neglegible_difference(dir):
    assert(compare_vtk(dir + "vtu.vtu", dir + "vtu4.vtu") == 0)


def test_close_to_zero_difference(dir):
    assert(compare_vtk(dir + "vtu5.vtu", dir + "vtu6.vtu") == 1)


def test_close_to_zero_difference_zerothreshold(dir):
    assert(compare_vtk(dir + "vtu5.vtu", dir + "vtu6.vtu", zeroValueThreshold={"small": 1e-20}) == 1)


def test_close_to_zero_difference_zerothreshold2(dir):
    assert(compare_vtk(dir + "vtu5.vtu", dir + "vtu6.vtu", zeroValueThreshold={"small": 1e-19}) == 0)
