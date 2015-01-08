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
# add_static_variants(SOURCE src1 [, src2 ..]
#                     BASENAME base
#                     INIFILE ini
#                     TARGETS output
#                    [DEBUG]
#                    )
# Given a meta ini file with a static section, add a set of
# executables representing all possible configurations. The naming
# scheme for the executable targets is: The given basename, followed
# by an underscore, followed by the special __exec_suffix key from
# the meta ini file. The sources for the targets (which for a system
# test are considered to be the same for all variants) can be given
# via the source parameter. The list of generated targets is stored in
# the given variable for further use. The list of currently handled
# subgroups in the static section is:
#   COMPILE_DEFINITIONS
#
# add_system_test_per_target(TARGET target1 [, target2 ..]
#                            INIFILE inifile)
#
# For a preconfigured set of targets, test targets are created. The inifile
# for the test is expanded into the build tree. The number of tests is
# the product of the number of executable targets and inifiles defined by
# the metainifile. The same meta inifile is used for all targets. Call
# multiple times for different behaviour.
#
# add_dune_system_test(TARGET target)

find_package(PythonInterp)

include(ParsePythonData)

function(add_static_variants)
  # parse the parameter list
  set(OPTION DEBUG)
  set(SINGLE BASENAME INIFILE TARGETS)
  set(MULTI SOURCE)
  cmake_parse_arguments(STATVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  # get the static information from the ini file
  # TODO maybe check whether an absolute path has been given for a mini file
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/python/static_metaini.py ${CMAKE_CURRENT_SOURCE_DIR}/${STATVAR_INIFILE}
                  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                  OUTPUT_VARIABLE output)
  parse_python_data(PREFIX STATINFO INPUT "${output}")

  # iterate over the static configurations
  foreach(conf ${STATINFO___CONFIGS})
    # add the executable with that configurations
    add_executable(${STATVAR_BASENAME}_${conf} "${STATVAR_SOURCE}")
    list(APPEND targetlist "${STATVAR_BASENAME}_${conf}")

    # TODO all groups to be recognized in the static section must be implemented here
    # similar to the compile definitions group.

    # treat compile definitions
    foreach(cd ${STATINFO___COMPILE_DEFINITIONS})
      set_property(TARGET ${STATVAR_BASENAME}_${conf} APPEND PROPERTY
                   COMPILE_DEFINITIONS "${cd}=${STATINFO_${conf}_COMPILE_DEFINITIONS_${cd}}")
    endforeach(cd ${STATINFO___COMPILE_DEFINITIONS})

    # maybe output debug information
    if(${STATVAR_DEBUG})
      message("Generated target ${STATVAR_BASENAME}_${conf}")
      get_property(cd TARGET ${STATVAR_BASENAME}_${conf} PROPERTY COMPILE_DEFINITIONS)
      message("  with COMPILE_DEFINITIONS: ${cd}")
    endif(${STATVAR_DEBUG})
  endforeach(conf ${STATINFO___CONFIGS})

  # export the list of created targets
  set(${STATVAR_TARGETS} "${targetlist}" PARENT_SCOPE)
endfunction(add_static_variants)

function(add_system_test_per_target)
  # parse arguments to function call
  set(OPTION DEBUG)
  set(SINGLE INIFILE)
  set(MULTI TARGET)
  cmake_parse_arguments(TARGVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  # expand the given meta ini file into the build tree
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/python/metaIni.py ${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE}
                  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                  OUTPUT_VARIABLE output)
  parse_python_data(PREFIX iniinfo INPUT "${output}")

  # add the tests for all targets
  foreach(target ${TARGVAR_TARGET})
    foreach(inifile ${iniinfo_names})
      if (${TARGVAR_DEBUG})
        message("Adding a target with executable ${target} and inifile ${inifile}")
      endif (${TARGVAR_DEBUG})

      # Somehow the test have to be named, although the naming scheme is not relevant for
      # the selection of tests to run on the server side. For the moment we combine the
      # executable target name with the ini file name.
      get_filename_component(ininame ${inifile} NAME)
      string(REGEX REPLACE "\\..*" "" ininame ${ininame})

      add_test(${target}_${ininame} ${target} ${inifile})
    endforeach(inifile ${iniinfo_names})
  endforeach(target ${TARGVAR_TARGET})
endfunction(add_system_test_per_target)

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
