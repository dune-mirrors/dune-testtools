Python documentation of dune-testools
*************************************

Modules of dune-testtools
=========================

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

.. currentmodule:: scripts
.. autosummary::
   :toctree: dune.testtools

   dune_expand_metaini
   dune_extract_static
   dune_has_static_section
   dune_metaini_analysis
