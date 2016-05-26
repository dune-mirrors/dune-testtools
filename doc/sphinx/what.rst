What is ``dune-testtools``?
***************************

``dune-testtools`` is a dune module developed by

- Timo Koch (timo.koch@iws.uni-stuttgart.de)
- Dominic Kempf (dominic.kempf@iwr.uni-heidelberg.de)

``dune-testtools`` provides the following components:

**A Python module**

- a domain specific language for feature modelling, which is
  naturally integrates into the workflow of numerical simulation.
- wrapper scripts to facilitate test result checking
- a CMake interface to communicate data to the build system
- a test suite to check ``dune-testtools``

**CMake macros**

- a one-macro solution for specifying system tests
- assertions for the buildsystem

How to use ``dune-testtools``?
==============================

Dune-testtools is written as a dune module. You can put it as a requirement into the dune.module file of your own module and configure/build it through dunecontrol (see the documentation of
`dune-common <https://gitlab.dune-project.org/core/dune-common>`_ for details).

Check the ```dune-testtools`` <https://gitlab.dune-project.org/quality/dune-testtools>`_ dune module
repository for more.

Where to get help?
==================

To get help concerning ``dune-testtools``, first check the technical
documentation in the doc subfolder. If your problem persists,
check the `bugtracker <https://gitlab.dune-project.org/quality/dune-testtools/issues>`_
or contact the authors directly.

.. note::
   There is no mailing list (yet).

Acknowledgments
===============

The work by Timo Koch and Dominic Kempf is supported by the
ministry of science, research and arts of the federal state of
Baden-Württemberg (Ministerium für Wissenschaft, Forschung
und Kunst Baden-Württemberg).