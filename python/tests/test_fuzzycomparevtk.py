""" A test for the vtu fuzzy compare"""
from __future__ import absolute_import
from dune_testtools.wrapper.fuzzy_compare_vtk import compare_vtk


def test_0(dir):
    assert(compare_vtk(dir + "vtu1.vtu", dir + "vtu2.vtu") == 0)


def test_1(dir):
    assert(compare_vtk(dir + "vtu1.vtu", dir + "vtu21.vtu") == 0)


def test_2(dir):
    assert(compare_vtk(dir + "vtu1.vtu", dir + "vtu3.vtu") == 0)


def test_3(dir):
    assert(compare_vtk(dir + "vtu1.vtu", dir + "vtu31.vtu") == 1)
