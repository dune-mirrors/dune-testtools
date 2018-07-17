![Build Status](https://gitlab.dune-project.org/quality/dune-testtools/badges/master/build.svg)

# What is dune-testtools?

dune-testtools provides the following components:
- a domain specific language for feature modelling, which is
  naturally integrates into the workflow of numerical simulation.
- Tools to test whether a given PDE discretization does still
  yield the correct result without performance (or scalability)
  regressions.
- Integration of above tools into a CMake based build system.
- Extensions to the dune core modules to support the development
  of system tests.

# How to use dune-testtools

dune-testtools is written as a Dune module. You can put it as a
requirement into the dune.module file of your own module and
configure/build it through dunecontrol (see the documentation
of dune-common for details).

# Where to get help

To get help concerning dune-testtools, first check the technical
documentation in the doc subfolder. If your problem persists,
check the bugtracker at

https://gitlab.dune-project.org/quality/dune-testtools/issues

or contact the authors directly:
*   Timo Koch (timo.koch@iws.uni-stuttgart.de)
*   Dominic Kempf (dominic.kempf@iwr.uni-heidelberg.de)

# Acknowledgments

The work by Timo Koch and Dominic Kempf is supported by the
ministry of science, research and arts of the federal state of
Baden-Württemberg (Ministerium für Wissenschaft, Forschung
und Kunst Baden-Württemberg).
