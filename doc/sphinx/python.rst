Python documentation of dune-testools
*************************************

The dune-testools Python module provides the infrstructure for parsing
and expanding meta ini files. Script for communicating information to
a CMake-based buildsystem are provided. It further provides test wrapper scripts
aiming at testing for specific quality measures.

Modules of dune-testtools
=========================

The dune-testtools core modules provide all functionality related
to meta ini files and their expansion mechanism.
Also have a look at the :ref:`introduction to meta ini files <introductionmetaini>`.

.. currentmodule:: dune.testtools
.. autosummary::
   :toctree: dune.testtools

   metaini
   cmakeoutput
   command_infrastructure
   command
   conditionals
   escapes
   parser
   static_metaini
   uniquenames
   writeini
   testdiscarding


.. _thewrappers:

Wrapper scripts of dune-testtools
=================================

dune-testtools provides test wrappers for checking specific quality aspects
of numerical software. Wrapper scripts are meant to be implemented by users
wishing to check a certain aspect of their test. However, the most common
test wrappers are already provided with dune-testools.

.. currentmodule:: wrapper
.. autosummary::
   :toctree: dune.testtools

   dune_execute
   dune_execute_parallel
   dune_outputtreecompare
   dune_vtkcompare
   dune_convergencetest


Helper modules for wrapper scripts
++++++++++++++++++++++++++++++++++

.. currentmodule:: dune.testtools.wrapper
.. autosummary::
   :toctree: dune.testtools

   argumentparser
   call_executable
   compareini
   convergencetest
   fuzzy_compare_vtk


Scripts of dune-testtools
=========================

dune-testtools provides a small selection of scripts. Most of the
scripts are used in the buildsystem integration and are called
through CMake at build time. They provide meta ini information
in a specific format to be parsed by CMake.

The script `dune_metaini_analysis` can be used to analyse
meta ini files and interactively inspect the configurations resulting
from expansion.

.. currentmodule:: scripts
.. autosummary::
   :toctree: dune.testtools

   dune_expand_metaini
   dune_extract_static
   dune_has_static_section
   dune_metaini_analysis
