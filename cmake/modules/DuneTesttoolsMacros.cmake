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
#                     CREATED_TARGETS output
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
# First Signature:
# add_dune_system_test(SOURCE src1 [, src2 ..]
#                      BASENAME base
#                      INIFILE ini
#                      CREATED_TARGETS output
#                     [SCRIPT script]
#                     [DEBUG]
#                     )
#
# Second Signature:
# add_dune_system_test(TARGET tar1 [, tar2 ..]
#                      INIFILE ini
#                     [CREATED_TARGETS output]
#                     [SCRIPT script]
#                     [DEBUG]
#                     )
#
# Offers a one-macro solution to both static and dynamic variants. All the parameters
# are a combination of the parameters of above two macros (TODO write again for clarity,
# once the interface is fixed).

find_package(PythonInterp)

# Check the found python version
if(PYTHON_VERSION_STRING VERSION_LESS 2.7)
  message(FATAL_ERROR "dune-testtools requires at least python 2.7")
endif()

# Check for the existence of the python-pyparsing package
if(NOT CMAKE_CROSSCOMPILING)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import pyparsing" RESULT_VARIABLE PYPARSING_RETURN)
  if(NOT PYPARSING_RETURN STREQUAL "0")
    message(FATAL_ERROR "dune-testtools requires the package python-pyparsing to be present on the system")
  endif()
else()
  message(WARNING "Cross-compilation warning: Assuming existence of python-pyparsing on the target system!")
endif()

find_package(MPI)

# Generate a string containing "DEBUG" if we want to debug macros
if(DEBUG_MACRO_TESTS)
  set(DEBUG_MACRO_TESTS DEBUG)
else()
  set(DEBUG_MACRO_TESTS)
endif()
include(DuneCMakeAssertion)

include(ParsePythonData)

function(add_static_variants)
  # parse the parameter list
  set(OPTION DEBUG)
  set(SINGLE BASENAME INIFILE CREATED_TARGETS)
  set(MULTI SOURCE)
  cmake_parse_arguments(STATVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(STATVAR_UNPARSED_ARGUMENTS)
    message(WARNING "add_static_variants: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # Configure a bogus file from the meta ini file. This is a trick to retrigger configuration on meta ini changes.
  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/${STATVAR_INIFILE} ${CMAKE_CURRENT_BINARY_DIR}/tmp_${STATVAR_INIFILE})

  # get the static information from the ini file
  # TODO maybe check whether an absolute path has been given for a mini file
  execute_process(COMMAND env PYTHONPATH=$PYTHONPATH:${DUNE_TESTTOOLS_PATH}/python ${PYTHON_EXECUTABLE} -m dune_testtools.static_metaini --ini ${CMAKE_CURRENT_SOURCE_DIR}/${STATVAR_INIFILE}
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
    if(NOT TARGET ${tname})
      add_executable(${tname} "${STATVAR_SOURCE}")

      # treat compile definitions
      foreach(cd ${STATINFO___COMPILE_DEFINITIONS})
        target_compile_definitions(${tname} PUBLIC "${cd}=${STATINFO_${conf}_${cd}}")
      endforeach()

      # maybe output debug information
      if(${STATVAR_DEBUG})
        message("Generated target ${tname}")
        get_property(cd TARGET ${tname} PROPERTY COMPILE_DEFINITIONS)
        message("  with COMPILE_DEFINITIONS: ${cd}")
      endif()
    endif()
    if(${STATVAR_DEBUG})
      message("Generating target ${tname} skipped because it already existed!")
    endif()
    list(APPEND targetlist "${tname}")
  endforeach()

  # export the list of created targets
  set(${STATVAR_CREATED_TARGETS} ${targetlist} PARENT_SCOPE)
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
    set(TARGVAR_SCRIPT ${DUNE_TESTTOOLS_PATH}/python/dune_testtools/wrapper/call_executable.py)
  endif()

  # expand the given meta ini file into the build tree
  execute_process(COMMAND env PYTHONPATH=$PYTHONPATH:${DUNE_TESTTOOLS_PATH}/python ${PYTHON_EXECUTABLE} -m dune_testtools.metaini --cmake --ini ${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE} --dir ${CMAKE_CURRENT_BINARY_DIR}
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
      # ugly CMake bug gets fixed by adding a random prefix to the compared strings
      if("compare_${TARGVAR_TARGETBASENAME}" STREQUAL "compare_${target}")
        set(DOSOMETHING TRUE)
      endif()
      if("compare_${TARGVAR_TARGETBASENAME}_${iniinfo_${inifile}_suffix}" STREQUAL "compare_${target}")
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

      # if the script contains the py extension remove it because we execute it as a module
      get_filename_component(module ${TARGVAR_SCRIPT} NAME_WE)

      if(${DOSOMETHING})
        if(NOT ${MPI_CXX_FOUND})
          add_test(NAME ${target}_${ininame}
                   COMMAND env PYTHONPATH=$PYTHONPATH:${DUNE_TESTTOOLS_PATH}/python ${PYTHON_EXECUTABLE} -m dune_testtools.wrapper.${module}
                    --exec ${target}
                    --ini "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}"
                    --source ${CMAKE_CURRENT_SOURCE_DIR}
                  )
        else()
          add_test(NAME ${target}_${ininame}
                   COMMAND env PYTHONPATH=$PYTHONPATH:${DUNE_TESTTOOLS_PATH}/python ${PYTHON_EXECUTABLE} -m dune_testtools.wrapper.${module}
                    --exec ${target}
                    --ini "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}"
                    --source ${CMAKE_CURRENT_SOURCE_DIR}
                    --mpi-exec "${MPIEXEC}"
                    --mpi-numprocflag=${MPIEXEC_NUMPROC_FLAG}
                    --mpi-preflags "${MPIEXEC_PREFLAGS}"
                    --mpi-postflags "${MPIEXEC_POSTFLAGS}"
                  )
        endif()
        set_property(TEST ${target}_${ininame} PROPERTY LABELS ${iniinfo_labels_${ininame}} DUNE_SYSTEMTEST)
        set_tests_properties(${target}_${ininame} PROPERTIES SKIP_RETURN_CODE "77")
      endif()
    endforeach()
  endforeach()
endfunction()

function(add_dune_system_test)
  # parse arguments
  set(OPTION DEBUG)
  set(SINGLE INIFILE BASENAME SCRIPT)
  set(MULTI SOURCE TARGET CREATED_TARGETS)
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
    set(SYSTEMTEST_SCRIPT call_executable)
  endif()

  # we provide two signatures: either a source(s) is given or a target(s)
  if(SYSTEMTEST_SOURCE AND SYSTEMTEST_TARGET)
    message(FATAL_ERROR "Use either the SOURCE or the TARGET signature!")
  endif()
  if(NOT SYSTEMTEST_SOURCE AND NOT SYSTEMTEST_TARGET)
    message(FATAL_ERROR "Specify either the SOURCE or the TARGET argument!")
  endif()

  if(SYSTEMTEST_SOURCE)
    # The above macros have been written in a way that allows us to use them
    # combined. The TARGETBASENAME parameter is introduced for that.
    add_static_variants(SOURCE ${SYSTEMTEST_SOURCE}
                        BASENAME ${SYSTEMTEST_BASENAME}
                        INIFILE ${SYSTEMTEST_INIFILE}
                        CREATED_TARGETS targetlist
                        ${DEBUG})

    # export the targetlist generated by add_static_variants
    set(${SYSTEMTEST_CREATED_TARGETS} ${targetlist} PARENT_SCOPE)

    add_system_test_per_target(INIFILE ${SYSTEMTEST_INIFILE}
                               TARGET ${targetlist}
                               SCRIPT ${SYSTEMTEST_SCRIPT}
                               ${DEBUG}
                               TARGETBASENAME ${SYSTEMTEST_BASENAME})
  else()
    execute_process(COMMAND env PYTHONPATH=$PYTHONPATH:${DUNE_TESTTOOLS_PATH}/python ${PYTHON_EXECUTABLE}
                    ${DUNE_TESTTOOLS_PATH}/python/scripts/has_static_section.py --ini ${CMAKE_CURRENT_SOURCE_DIR}/${SYSTEMTEST_INIFILE}
                    RESULT_VARIABLE res)
    if(${res})
      message(STATUS "The meta ini file specifies static variations!")
      message(FATAL_ERROR "The TARGET signature can be only used for dynamic variations.")
    endif()

    if(SYSTEMTEST_BASENAME)
      message(WARNING "A BASENAME is given for the TARGET signature. The argument is ignored!")
    endif()
    # the target signature is effectively a convenience function for the dyanmic macro
    # be careful not to have a static section in the meta ini file!
    set(${SYSTEMTEST_CREATED_TARGETS} ${SYSTEMTEST_TARGET} PARENT_SCOPE)
    add_system_test_per_target(INIFILE ${SYSTEMTEST_INIFILE}
                               TARGET ${SYSTEMTEST_TARGET}
                               SCRIPT ${SYSTEMTEST_SCRIPT}
                               ${DEBUG})
  endif()
endfunction()
