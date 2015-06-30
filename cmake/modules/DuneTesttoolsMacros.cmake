# File for module specific CMake functions.
#
# This file defines the function add_dune_system_test and the function
# add_dune_convergence_test
#
# These functions could in the long run be the interface
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
#                            INIFILE inifile
#                           [SCRIPT script]
#                           [TARGETBASENAME basename])
#
# For a preconfigured set of targets, test targets are created. The inifile
# for the test is expanded into the build tree. The number of tests is
# the product of the number of executable targets and inifiles defined by
# the metainifile. The same meta inifile is used for all targets. Call
# multiple times for different behaviour.
# The SCRIPT parameter is used to put a python wrapper script around the
# C++ executable. This can for example be used to have the test result depend
# on a vtk comparison. See dune-testtools/python/wrapper for predefined such
# wrapper scripts.
# The TARGETBASENAME parameter is used internally, to check whether an ini file
# is matching a given executable.
#
# add_dune_system_test(SOURCE src1 [, src2 ..]
#                      BASENAME base
#                      INIFILE ini
#                      TARGETS output
#                     [SCRIPT script]
#                     [DEBUG]
#                     )
# Offers a one-macro solution to both static and dynamic variants. All the parameters
# are a combination of the parameters of above two macros (TODO write again for clarity,
# once the interface is fixed).
#
# add_convergence_test_per_target(TARGET target1 [, target2 ..]
#                                 INIFILE inifile
#                                 [SCRIPT script]
#                                 [TARGETBASENAME basename]
#                                 [DEBUG])
#
# For a preconfigured set of targets, convergence tests are created. The inifile
# for the test is expanded into the build tree. The number of tests is
# the product of the number of executable targets and inifiles defined by
# the metainifile. Each test consists of several runs defined by the TestKey in the metaini file.
# The same meta inifile is used for all targets. Call
# multiple times for different behaviour.
# The SCRIPT parameter is used to put a python wrapper script around the
# C++ executable for each execution within one convergence test.
# The TARGETBASENAME parameter is used internally, to check whether an ini file
# is matching a given executable.
#
# add_dune_convergence_test(SOURCE src1 [, src2 ..]
#                      BASENAME base
#                      INIFILE ini
#                      TARGET target1 [, target2 ..]
#                      OUTPUT_TARGETS outputtargetlist
#                     [SCRIPT script]
#                     [DEBUG]
#                     )
# Offers a one-macro solution to add a convergence test with static and dynamic variants.
# Either a SOURCE or a TARGET can be specified. Both can also be lists of sources or targets.
# In case a target is specified the target is used to generate convergence tests by dynamic
# variations of the data in the metaini file. Internally the add_convergence_test_per_target
# macro is called. When specifying a source instead, executables are built with the
# add_static_variants macro. These executables are then used to generate the convergence tests
# by using the add_convergence_test_per_target macro.
# The OUTPUT_TARGETS variables can be used to get a list of all internally created targets. In
# case of specifying a target this will be the target itself. In case of specifying a source, this
# will be a list of all created targets.

find_package(PythonInterp)

# Check the found python version
if(PYTHON_VERSION_STRING VERSION_LESS 2.7)
  message(FATAL_ERROR "dune-testtools requires at least python 2.7")
endif()

# Check for the existence of the python-pyparsing package
if(NOT CMAKE_CROSSCOMPILING)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import pyparsing" RESULT_VARIABLE PYPARSING_RETURN)
  message("PYPARSING_RETURN: ${PYPARSING_RETURN}")
  if(NOT PYPARSING_RETURN STREQUAL "0")
    message(FATAL_ERROR "dune-testtools requires the package python-pyparsing to be present on the system")
  endif()
else()
  message(WARNING "Cross-compilation warning: Assuming existence of python-pyparsing on the target system!")
endif()

include(ParsePythonData)

function(add_static_variants)
  # parse the parameter list
  set(OPTION DEBUG)
  set(SINGLE BASENAME INIFILE TARGETS)
  set(MULTI SOURCE)
  cmake_parse_arguments(STATVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(STATVAR_UNPARSED_ARGUMENTS)
    message(WARNING "add_static_variants: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # get the static information from the ini file
  # TODO maybe check whether an absolute path has been given for a mini file
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${DUNE_TESTTOOLS_PATH}/python/static_metaini.py --ini ${CMAKE_CURRENT_SOURCE_DIR}/${STATVAR_INIFILE}
                  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                  OUTPUT_VARIABLE output)
  parse_python_data(PREFIX STATINFO INPUT "${output}")

  # iterate over the static configurations
  foreach(conf ${STATINFO___CONFIGS})
    # determine the target name: in case of only one config, omit the underscore.
    set(tname ${STATVAR_BASENAME})
    if(NOT ${conf} STREQUAL "__empty")
      set(tname ${tname}_${conf})
    endif()
    # add the executable with that configurations
    add_executable(${tname} "${STATVAR_SOURCE}")
    list(APPEND targetlist "${tname}")

    # TODO all groups to be recognized in the static section must be implemented here
    # similar to the compile definitions group.

    # treat compile definitions
    foreach(cd ${STATINFO___COMPILE_DEFINITIONS})
      set_property(TARGET ${tname} APPEND PROPERTY
        COMPILE_DEFINITIONS "${cd}=${STATINFO_${conf}_COMPILE_DEFINITIONS_${cd}}")
    endforeach()

    # maybe output debug information
    if(${STATVAR_DEBUG})
      message("Generated target ${tname}")
      get_property(cd TARGET ${tname} PROPERTY COMPILE_DEFINITIONS)
      message("  with COMPILE_DEFINITIONS: ${cd}")
    endif()
  endforeach()

  # export the list of created targets
  set(${STATVAR_TARGETS} ${targetlist} PARENT_SCOPE)
endfunction()

function(add_system_test_per_target)
  # parse arguments to function call
  set(OPTION DEBUG)
  set(SINGLE INIFILE SCRIPT TARGETBASENAME)
  set(MULTI TARGET)
  cmake_parse_arguments(TARGVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(TARGVAR_UNPARSED_ARGUMENTS)
    message(WARNING "add_system_test_per_target: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # set a default for the script. call_executable.py just calls the executable.
  # There, it is also possible to hook in things depending on the inifile
  if(NOT TARGVAR_SCRIPT)
    set(TARGVAR_SCRIPT ${DUNE_TESTTOOLS_PATH}/python/wrapper/call_executable.py)
  endif()

  # expand the given meta ini file into the build tree
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${DUNE_TESTTOOLS_PATH}/python/metaini.py --cmake --ini ${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE} --dir ${CMAKE_CURRENT_BINARY_DIR}
                  OUTPUT_VARIABLE output)

  parse_python_data(PREFIX iniinfo INPUT "${output}")

  # add the tests for all targets
  foreach(target ${TARGVAR_TARGET})
    foreach(inifile ${iniinfo_names})
      if(${TARGVAR_DEBUG})
        message("  Adding a target with executable ${target} and inifile ${inifile}...")
      endif()

      # Somehow the test have to be named, although the naming scheme is not relevant for
      # the selection of tests to run on the server side. For the moment we combine the
      # executable target name with the ini file name.
      get_filename_component(ininame ${inifile} NAME_WE)

      # check whether something needs to be done. This is either when our target is matching
      # the given suffix, or when TARGETBASENAME isnt given (this indicates stand-alone usage)
      # or in case no suffix is given (we have only one target) when the target is matching the
      # target basename
      set(DOSOMETHING FALSE)
      if("${TARGVAR_TARGETBASENAME}" STREQUAL "${target}")
        set(DOSOMETHING TRUE)
      endif()
      if("${TARGVAR_TARGETBASENAME}_${iniinfo_${inifile}_suffix}" STREQUAL "${target}")
        set(DOSOMETHING TRUE)
      endif()
      if(NOT DEFINED TARGVAR_TARGETBASENAME)
        set(DOSOMETHING TRUE)
      endif()

      if(${TARGVAR_DEBUG})
        message("  -- ${DOSOMETHING}")
      endif()

      # get the extension of the ini file (can be user defined)
      get_filename_component(iniext ${inifile} EXT)

      if(${DOSOMETHING})
        add_test(NAME ${target}_${ininame}
                 COMMAND env PYTHONPATH=$PYTHONPATH:${DUNE_TESTTOOLS_PATH}/python ${PYTHON_EXECUTABLE} ${TARGVAR_SCRIPT}
                    --exec ${target}
                    --ini "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}"
                    --source ${CMAKE_CURRENT_SOURCE_DIR}
                )
      endif()
    endforeach()
  endforeach()
endfunction()

function(add_dune_system_test)
  # parse arguments
  set(OPTION DEBUG)
  set(SINGLE INIFILE BASENAME SCRIPT)
  set(MULTI SOURCE TARGETS)
  cmake_parse_arguments(SYSTEMTEST "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(SYSTEMTEST_UNPARSED_ARGUMENTS)
    message(WARNING "add_dune_system_test: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # construct a string containg DEBUG to pass the debug flag to the other macros
  set(DEBUG "")
  if(SYSTEMTEST_DEBUG)
    set(DEBUG "DEBUG")
  endif()

  # set a default for the script. call_executable.py just calls the executable.
  # There, it is also possible to hook in things depending on the inifile
  if(NOT SYSTEMTEST_SCRIPT)
    set(SYSTEMTEST_SCRIPT ${DUNE_TESTTOOLS_PATH}/python/wrapper/call_executable.py)
  endif()

  # The above macros have been written in a way that allows us to use them
  # combined. The TARGETBASENAME parameter is introduced for that.

  add_static_variants(SOURCE ${SYSTEMTEST_SOURCE}
                      BASENAME ${SYSTEMTEST_BASENAME}
                      INIFILE ${SYSTEMTEST_INIFILE}
                      TARGETS targetlist
                      ${DEBUG})

  # export the targetlist generated by add_static_variants
  set(${SYSTEMTEST_TARGETS} ${targetlist} PARENT_SCOPE)

  add_system_test_per_target(INIFILE ${SYSTEMTEST_INIFILE}
                             TARGET ${targetlist}
                             SCRIPT ${SYSTEMTEST_SCRIPT}
                             ${DEBUG}
                             TARGETBASENAME ${SYSTEMTEST_BASENAME})

endfunction()

function(add_convergence_test_per_target)
  # parse arguments to function call
  set(OPTION DEBUG)
  set(SINGLE INIFILE SCRIPT TARGETBASENAME)
  set(MULTI TARGET)
  cmake_parse_arguments(TARGVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(TARGVAR_UNPARSED_ARGUMENTS)
    message(WARNING "add_convergence_test_per_target: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()
  # set a default for the script. call_executable.py just calls the executable.
  # There, it is also possible to hook in things depending on the inifile
  if(NOT TARGVAR_SCRIPT)
    set(TARGVAR_SCRIPT ${DUNE_TESTTOOLS_PATH}/python/wrapper/call_executable.py)
  endif()

  # expand the given meta ini file into the build tree
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${DUNE_TESTTOOLS_PATH}/python/convergencetest_metaini.py 
                    --cmake --ini ${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE} --dir ${CMAKE_CURRENT_BINARY_DIR}
                    OUTPUT_VARIABLE output)

  parse_python_data(PREFIX iniinfo INPUT "${output}")

  # add the tests for all targets
  foreach(target ${TARGVAR_TARGET})
    foreach(test ${iniinfo_tests})
      # initialize variable holding ini files
      set(convergence_test_inis "")
      # loop over ini files needed for one test
      foreach(inifile ${iniinfo_names})
        # Somehow the test have to be named, although the naming scheme is not relevant for
        # the selection of tests to run on the server side. For the moment we combine the
        # executable target name with the ini file name.
        get_filename_component(ininame ${inifile} NAME_WE)

        if(${TARGVAR_DEBUG})
          message("  Adding a target to test ${test} with executable ${target} and inifile ${ininame}...")
        endif()

        # check whether something needs to be done. This is either when our target is matching
        # the given suffix, or when TARGETBASENAME isnt given (this indicates stand-alone usage)
        # or in case no suffix is given (we have only one target) when the target is matching the
        # target basename
        set(DOSOMETHING FALSE)
        if("${TARGVAR_TARGETBASENAME}" STREQUAL "${target}")
          set(DOSOMETHING TRUE)
        endif()
        if("${TARGVAR_TARGETBASENAME}_${iniinfo_${test}_${inifile}_suffix}" STREQUAL "${target}")
          set(DOSOMETHING TRUE)
        endif()
        if(NOT DEFINED TARGVAR_TARGETBASENAME)
          set(DOSOMETHING TRUE)
        endif()

        if(${TARGVAR_DEBUG})
          message("  -- ${DOSOMETHING}")
        endif()

        # get the extension of the ini file (can be user defined)
        get_filename_component(iniext ${inifile} EXT)

        if(${DOSOMETHING})
          # add the inifile to the list of ini files for this target
          list(APPEND convergence_test_inis "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}")
        endif()
      endforeach()

      if(NOT "${convergence_test_inis}" STREQUAL "")
        # convert list to plus seperated string
        # trick to hand over list as an argument that cmake expands by default to a set of single strings
        string(REPLACE ";" "+" inis "${convergence_test_inis}")
        # add the test
        # TODO why do I need to pass the testtools patch and the python executable?
        add_test(NAME "convergence_test_${target}_${test}" COMMAND "${CMAKE_COMMAND}"
                                      -DCONVERGENCE_TEST_TARGET=${target}
                                      -DCONVERGENCE_TEST_INIS=${inis}
                                      -DCONVERGENCE_TEST_ID=${test}
                                      -DCONVERGENCE_TEST_META_INI=${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE}
                                      -DCONVERGENCE_TEST_SCRIPT=${TARGVAR_SCRIPT}
                                      -DDUNE_TESTTOOLS_PATH=${DUNE_TESTTOOLS_PATH}
                                      -DPYTHON_EXECUTABLE=${PYTHON_EXECUTABLE}
                                      -P "${DUNE_TESTTOOLS_PATH}/cmake/modules/RunConvergenceTest.cmake"
                                      )
        if(${TARGVAR_DEBUG})
          message(STATUS "Added convergence test: convergence_test_${target}_${test}")
        endif()
      endif()
    endforeach()
  endforeach()
endfunction()

function(add_dune_convergence_test)
  # parse arguments
  set(OPTION DEBUG)
  set(SINGLE INIFILE BASENAME SCRIPT)
  set(MULTI SOURCE TARGET OUTPUT_TARGETS)
  cmake_parse_arguments(CONVERGENCETEST "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(CONVERGENCETEST_UNPARSED_ARGUMENTS)
    message(WARNING "add_dune_convergence_test: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # construct a string containg DEBUG to pass the debug flag to the other macros
  set(DEBUG "")
  if(CONVERGENCETEST_DEBUG)
    set(DEBUG "DEBUG")
  endif()

  # set a default for the script. call_executable.py just calls the executable.
  # There, it is also possible to hook in things depending on the inifile
  if(NOT CONVERGENCETEST_SCRIPT)
    set(CONVERGENCETEST_SCRIPT ${DUNE_TESTTOOLS_PATH}/python/wrapper/call_executable.py)
  endif()

  # throw an error if we neither SOURCE nor TARGET given.
  if(NOT CONVERGENCETEST_SOURCE AND NOT CONVERGENCETEST_TARGET)
    message(FATAL_ERROR "Please specify either a SOURCE or a TARGET.")
  endif()

  # we either expect a source/sources OR a target/targetlist
  if(CONVERGENCETEST_SOURCE AND NOT CONVERGENCETEST_TARGET)
    add_static_variants(SOURCE ${CONVERGENCETEST_SOURCE}
                        BASENAME ${CONVERGENCETEST_BASENAME}
                        INIFILE ${CONVERGENCETEST_INIFILE}
                        TARGETS targets
                        ${DEBUG})

    # export the targetlist generated by add_static_variants
    set(${CONVERGENCETEST_OUTPUT_TARGETS} ${targets} PARENT_SCOPE)

    add_convergence_test_per_target(INIFILE ${CONVERGENCETEST_INIFILE}
                                    TARGET ${targets}
                                    ${DEBUG}
                                    TARGETBASENAME ${CONVERGENCETEST_BASENAME}
                                    SCRIPT ${CONVERGENCETEST_SCRIPT})

  elseif(CONVERGENCETEST_TARGET AND NOT CONVERGENCETEST_SOURCE)
    # export the targetlist to have the full interface functionality
    set(${CONVERGENCETEST_OUTPUT_TARGETS} ${CONVERGENCETEST_TARGET} PARENT_SCOPE)

    add_convergence_test_per_target(INIFILE ${CONVERGENCETEST_INIFILE}
                                    TARGET ${CONVERGENCETEST_TARGET}
                                    ${DEBUG}
                                    TARGETBASENAME ${CONVERGENCETEST_BASENAME}
                                    SCRIPT ${CONVERGENCETEST_SCRIPT})

  else(CONVERGENCETEST_SOURCE AND NOT CONVERGENCETEST_TARGET)
    message(FATAL_ERROR "Both SOURCE and TARGET was specified. Ambiguous input.")
  endif(CONVERGENCETEST_SOURCE AND NOT CONVERGENCETEST_TARGET)
endfunction()
