Full documentation of dune-testtools
************************************
.. automodule:: dune_testtools

The dune-testtools core modules
===============================

The metaini module
++++++++++++++++++

.. automodule:: dune_testtools.metaini
    :members: expand_meta_ini

Other modules
+++++++++++++

.. automodule:: dune_testtools.cmakeoutput
    :members:
    :undoc-members:

.. automodule:: dune_testtools.command_infrastructure
    :members:
    :undoc-members:

.. automodule:: dune_testtools.command
    :members:
    :undoc-members:

.. automodule:: dune_testtools.conditionals
    :members:
    :undoc-members:

.. automodule:: dune_testtools.dotdict
    :members:
    :undoc-members:

.. automodule:: dune_testtools.escapes
    :members:
    :undoc-members:

.. automodule:: dune_testtools.parser
    :members:
    :undoc-members:

.. automodule:: dune_testtools.fuzzy_compare_vtk
    :members:
    :undoc-members:

.. automodule:: dune_testtools.static_metaini
    :members:
    :undoc-members:

.. automodule:: dune_testtools.uniquenames
    :members:
    :undoc-members:

.. automodule:: dune_testtools.writeini
    :members:
    :undoc-members:

The dune-testtools wrapper modules
==================================

.. automodule:: dune_testtools.wrapper

.. automodule:: dune_testtools.wrapper.call_executable
    :members:
    :undoc-members:

.. automodule:: dune_testtools.wrapper.call_parallel
    :members:
    :undoc-members:

.. automodule:: dune_testtools.wrapper.vtkcompare
    :members:
    :undoc-members:

.. automodule:: dune_testtools.wrapper.argumentparser
    :members:
    :undoc-members:

.. automodule:: dune_testtools.wrapper.convergencetest
    :members:
    :undoc-members:

The dune-testtools scripts
==========================

Write something about the scripts and what they do. Scripts can't be autodocumented because they are not importable.

What is dune-testtools?
=======================

dune-testtools is a python module developed by

- Timo Koch (timo.koch@iws.uni-stuttgart.de)
- Dominic Kempf (dominic.kempf@iwr.uni-heidelberg.de)

dune-testtools provides the following components

- a domain specific language for feature modelling, which is
  naturally integrates into the workflow of numerical simulation.
- wrapper scripts to facilitate test result checking
- a CMake interface to communicate data to the build system
- a test suite to check dune-testtools

How to use dune-testtools
+++++++++++++++++++++++++

dune-testtools is a python module that is included in a
dune-module. See the `dune-testtools <http://conan2.iwr.uni-heidelberg.de/git/quality/dune-testtools>`_ dune module for more.

Where to get help?
++++++++++++++++++

To get help concerning dune-testtools, first check the technical
documentation in the doc subfolder. If your problem persists,
check the `bugtracker <http://conan2.iwr.uni-heidelberg.de/git/quality/dune-testtools/issues>`_
or contact the authors directly.

.. note::
   There is no mailing list (yet).

Acknowledgments
+++++++++++++++

The work by Timo Koch and Dominic Kempf is supported by the
ministry of science, research and arts of the federal state of
Baden-Württemberg (Ministerium für Wissenschaft, Forschung
und Kunst Baden-Württemberg).

