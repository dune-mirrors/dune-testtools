"""
Allow to specify the discardal of tests based on CMake variables from the meta ini file.
Consider the following example:

[__static]
GRID = Yaspgrid<2>, UGGrid<2> | expand grid

Any test based on UG should be discarded if HAVE_UG is not true.
This is not possible in the cc file anymore, as it is written
generically.

This file introduces a solution approach quite similar to the 'exclude'
command for constraints. The corresponding command is called 'cmake_guard'.
Whenever the given condition evaluates to false in CMake, the test is discarded
(aka not added to the testing suite). Note that you may have several such
command lines: The test will be discarded if any of them evaluates to false.

To above example add the following line:
1, HAVE_UG | expand grid | cmake_guard
"""

from __future__ import absolute_import
from dune.testtools.command import meta_ini_command, CommandType


@meta_ini_command(name='cmake_guard')
def _cmake_guard(key=None, config=None):
    newkey = key.replace('__local.conditionals', '__cmake_guards')
    config[newkey] = config[key]
