# The cmake code to execute whenever a module requires or suggests dune-testtools.
#
# A summary of what is done:
#
# * Requirements on the python interpreter are formulated
# * The API for Dune-style system tests is included.
#
# .. cmake_variable:: DEBUG_MACRO_TESTS
#
#    If turned on, the configure time unit tests of dune-testtools
#    have verbose output. This is mainly useful if you are developing
#    and debugging dune-testtools.
#

dune_require_python_version(2.7)
#TODO: What is our minimum python3.x requirement?

# Generate a string containing "DEBUG" if we want to debug macros
if(DEBUG_MACRO_TESTS)
  set(DEBUG_MACRO_TESTS DEBUG)
else()
  set(DEBUG_MACRO_TESTS)
endif()

# Set the default on the variable DUNE_MAX_TEST_CORES
# Starting with Dune 3.0 this is done in dune-common
if(NOT DUNE_MAX_TEST_CORES)
  set(DUNE_MAX_TEST_CORES 1000000000)
endif()

# Discard all parallel tests if MPI was not found
if(NOT MPI_FOUND)
  set(DUNE_MAX_TEST_CORES 1)
endif()

include(DuneCMakeAssertion)
include(ParsePythonData)
include(DuneSystemtests)
include(ExpandMetaIni)
