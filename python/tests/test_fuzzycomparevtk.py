""" A test for the vtu fuzzy compare"""

from fuzzy_compare_vtk import *

def test_vtu1_vtu2():
	assert(is_fuzzy_equal_vtk("./tests/vtu1.vtu", "./tests/vtu2.vtu") == 0)
	assert(is_fuzzy_equal_vtk("./tests/vtu1.vtu", "./tests/vtu21.vtu") == 1)

#TODO fails because different grid ordering is not implemented yet
def test_vtu1_vtu3():
	#assert(is_fuzzy_equal_vtk("./tests/vtu1.vtu", "./tests/vtu3.vtu") == 0)	
	assert(is_fuzzy_equal_vtk("./tests/vtu1.vtu", "./tests/vtu31.vtu") == 1)