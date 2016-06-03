"""Allow to specify the discardal of tests based on CMake variables from the meta ini file.

.. currentmodule:: dune.testtools.testdiscarding

Consider the following example:

.. code-block:: ini

    [__static]
    GRID = Yaspgrid<2>, UGGrid<2> | expand grid

Any test based on ``UGGrid`` should be discarded if ``HAVE_UG`` is not ``true``.
This is not possible in the ``*.cc`` file anymore, as it is written
generically.

This file introduces a solution approach quite similar to the ``exclude``
command for constraints. The corresponding command is called ``cmake_guard``.

Commands
++++++++

.. _cmake_discard:
.. metaini_command:: cmake_guard
    :operates_on_value:

    Whenever the given condition evaluates to ``false`` in CMake, the test is discarded
    (aka not added to the testing suite). In contrast of what you might know from the
    ``label`` or ``exclude`` command the value gets evaluated in CMake. It is thus
    important to keep the statement as simple as possible, see the example.

    .. note::
        You may have several such command lines:
        The test will be discarded if any of them evaluates to false.

    Example:

    To above example add the following line:

    .. code-block:: ini

        1, HAVE_UG | expand grid | cmake_guard

    Tests using ``UGGrid`` will now be discarded if ``HAVE_UG`` is set to ``false``,
    i.e. if ``UGGrid`` was not found on your system. Tests using ``YaspGrid`` will
    always be added, since ``1`` evaluates to ``true``.

"""

from __future__ import absolute_import
from dune.testtools.command import meta_ini_command, CommandType


@meta_ini_command(name='cmake_guard')
def _cmake_guard(key=None, config=None):
    """Defines the meta ini command ``cmake_guard``"""
    newkey = key.replace('__local.conditionals', '__cmake_guards')
    config[newkey] = config[key]
