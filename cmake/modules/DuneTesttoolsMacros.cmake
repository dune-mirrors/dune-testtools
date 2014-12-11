# File for module specific CMake functions.
#
# This file defines the function add_dune_system_test.
#
# That function could in the long run be the interface
# which the user is seeing the automated testing through.
# It should use CMakeParseArguments to actually have
# a keyword argument style interface and be easy to handle.
# Given an executable and some flags, it will then add a whole
# number of tests with the correct labels and wrappers scripts
# applied.
#
# the synopsis should be kept up to date.
# SYNOPSIS:
#
# add_dune_system_test(TARGET target)

find_package(PythonInterp)

include(MetaIniMacros)
include(ConditionalIncludes)

function(add_dune_system_test)
  # define what kind of parameters can be given to this function
  # options don't take any arguments
  set(options)
  # parameters that are followed by exactly one argument
  set(oneValueArgs METAFILE BASENAME)
  # parameters that are followed by mutiple arguments
  set(multiValueArgs SOURCE)
  # the call that parses the arguments and sets variables
  # all set variables start with the prefix DUNE_SYSTEM_TEST
  # and are followed by an underscore and the above parameter name
  cmake_parse_arguments(DUNE_SYSTEM_TEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

  # expand the given meta ini file
  expand_meta_ini(METAFILE ${DUNE_SYSTEM_TEST_METAFILE} RETURNSTR output)

  # process the information obtained from the pyhton script.
  # first: escape all semicolons!
  message("output: ${output}")
  string(REGEX MATCHALL "[^\n]+" outputlist ${output})
  #string(REPLACE ";" "\;" output ${output})
  message("output: ${outputlist}")

  foreach(config ${outputlist})
    # turn the item into a list
   # message("Input: ${config}")
    string(REGEX MATCHALL "[^&]+" deflist ${config})
   # message("List: ${deflist}")
    #string(REPLACE "&" ";" config ${config})
   # message("Replaced: ${config}")
   # set(suffix "")
    list(GET deflist 0 suffix)
    #message("The suffix ${suffix}")
    list(REMOVE_ITEM deflist 0)
    set(target "${DUNE_SYSTEM_TEST_BASENAME}${suffix}")
    message("Generating target ${target}")

    # generate the actual target
    add_executable(${target} ${DUNE_SYSTEM_TEST_SOURCE})
    set_property(TARGET ${target} PROPERTY COMPILE_DEFINITIONS ${deflist})
  endforeach(config ${outputlist})
endfunction(add_dune_system_test)
