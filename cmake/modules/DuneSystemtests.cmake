# Define the API to add system tests in Dune.
#
# .. cmake_function:: add_static_variants
#
#    .. cmake_param:: SOURCE
#       :multi:
#       :required:
#
#       The source files for the executables to generate.
#
#    .. cmake_param:: BASENAME
#       :single:
#       :required:
#
#       The basename for the given executables. The names of the
#       actual executables is generated by appending the `__exec_suffix`
#       key from the meta ini file to this basename (underscore separated).
#       Try to avoid using a given basename more than once in a project.
#
#    .. cmake_param:: INIFILE
#       :single:
#       :required:
#
#       The meta ini file, whose `__static` section is used to
#       define the executables to add. See :ref:`introductionmetaini`
#       for details on how to write such meta ini files.
#
#    .. cmake_param:: CREATED_TARGETS
#       :single:
#       :required:
#
#       Variable to store the list of generated targets in the outer scope.
#       Use this to manually tune generated targets after generation.
#
#    .. cmake_param:: DEBUG
#       :option:
#
#       Set this option to get verbose output from the generation process.
#
#    Create a number of executables from the static information given in
#    meta ini file. The special section `__static` of the meta ini file is
#    relevant for this. Any variables you define in that section are interpreted
#    as preprocessor definitions.
#
# .. cmake_function:: add_system_test_per_target
#
#    .. cmake_param:: TARGET
#       :multi:
#       :required:
#
#       The target that specifies the executable that should be used for
#       the test. If multiple targets are given, each of them will be connected
#       with each ini file.
#
#    .. cmake_param:: INIFILE
#       :single:
#       :required:
#
#       The meta ini file, that describes the dynamic
#       variations of the systemtest. See :ref:`introductionmetaini`
#       for details on how to write such meta ini files.
#
#    .. cmake_param:: SCRIPT
#       :single:
#
#       The Python wrapper script around the test. Defaults to :code:`call_executable.py`,
#       which essentially forwards the return code of the program run.
#       Changing this parameter to a different Python wrapper enables more
#       involved, numerics-aware testing methods. Check :ref:`thewrappers`
#       for details on pre-implemented tools and on how to
#       write your own ones.
#
#    .. cmake_param:: TARGETBASENAME
#       :single:
#
#       This parameter is only for internal usage.
#
#    Given a set of executables (given as CMake targets), a number of tests is
#    added. The given meta ini file is expanded and each dynamic variant is
#    connected with each given executable.
#
# .. cmake_function:: dune_add_system_test
#
#    .. cmake_param:: SOURCE
#       :multi:
#       :required:
#
#       The source files for the executables to generate.
#
#    .. cmake_param:: BASENAME
#       :single:
#       :required:
#
#       The basename for the generated tests. The names of the
#       actual tests is generated by concatenating the
#       key from the meta ini file to this basename (underscore separated).
#       Try to avoid using a given basename more than once in a project.
#
#    .. cmake_param:: INIFILE
#       :single:
#       :required:
#
#       The meta ini file, that describes the dynamic and static
#       variations of the systemtest. See :ref:`introductionmetaini`
#       for details on how to write such meta ini files.
#
#    .. cmake_param:: CREATED_TARGETS
#       :single:
#       :required:
#
#       Variable to store the list of generated targets in the outer scope.
#       Use this to manually tune generated targets after generation.
#
#    .. cmake_param:: SCRIPT
#       :single:
#
#       The Python wrapper script around the test. Defaults to :code:`call_executable.py`,
#       which essentially forwards the return code of the program run.
#       Changing this parameter to a different Python wrapper enables more
#       involved, numerics-aware testing methods. Check :ref:`thewrappers` for details
#       on pre-implemented tools and on how to write your own ones.
#
#    .. cmake_param:: DEBUG
#       :option:
#
#       Set this option to get verbose output from the generation process.
#
#    .. cmake_param:: NO_TESTS
#       :option:
#
#       Set to avoid the adding of tests. Used to implement :ref:`dune_expand_metaini`.
#
#    A one-line solution to adding system tests to the build system.
#    Internally, this reuses the functions :ref:`add_static_variants` and
#    :ref:`add_system_test_per_target`.
#

function(add_static_variants)
  # parse the parameter list
  set(OPTION DEBUG)
  set(SINGLE BASENAME INIFILE CREATED_TARGETS)
  set(MULTI SOURCE)
  cmake_parse_arguments(STATVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(STATVAR_UNPARSED_ARGUMENTS)
    message(WARNING "add_static_variants: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # Allow absolute paths to the ini file
  if(NOT IS_ABSOLUTE ${STATVAR_INIFILE})
    set(STATVAR_INIFILE ${CMAKE_CURRENT_SOURCE_DIR}/${STATVAR_INIFILE})
  endif()

  # Configure a bogus file from the meta ini file. This is a trick to retrigger configuration on meta ini changes.
  string(REPLACE "/" "_" BOGUSFILE "tmp_${STATVAR_INIFILE}")
  configure_file(${STATVAR_INIFILE} ${CMAKE_CURRENT_BINARY_DIR}/${BOGUSFILE})

  # get the static information from the ini file
  # TODO maybe check whether an absolute path has been given for a mini file
  dune_execute_process(COMMAND ${CMAKE_BINARY_DIR}/run-in-dune-env dune_extract_static.py
                               --ini ${STATVAR_INIFILE}
                               --file ${CMAKE_CURRENT_BINARY_DIR}/interface.log
                       WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                       ERROR_MESSAGE "Error extracting static info from ${STATVAR_INIFILE}")
  parse_python_data(PREFIX STATINFO FILE ${CMAKE_CURRENT_BINARY_DIR}/interface.log)

  # If there is more than one configuration, introduce a meta target
  # that collects all these static variants
  if(NOT "${STATINFO___CONFIGS}" STREQUAL "__empty")
    add_custom_target(${STATVAR_BASENAME})
  endif()

  # iterate over the static configurations
  foreach(conf ${STATINFO___CONFIGS})
    # determine the target name: in case of only one config, omit the underscore.
    set(tname ${STATVAR_BASENAME})
    if(NOT ${conf} STREQUAL "__empty")
      set(tname ${tname}_${conf})
    endif()
    # add the executable with that configurations
    if(NOT TARGET ${tname})
      # evaluate all the discarding conditions that have been provided!
      set(SOURCE_FILES ${STATVAR_SOURCE})
      foreach(condition ${STATINFO_${conf}___GUARDS})
        separate_arguments(condition)
        if(NOT ${condition})
          # This test is to be skipped, we switch the source for a dummy that always return 77.
          if(CMAKE_PROJECT_NAME STREQUAL dune-testtools)
            set(SOURCE_FILES ${CMAKE_SOURCE_DIR}/cmake/scripts/main77.cc)
          else()
            set(SOURCE_FILES ${dune-testtools_PREFIX}/cmake/scripts/main77.cc)
          endif()
        endif()
      endforeach()

      add_executable(${tname} "${SOURCE_FILES}")

      # Add dependency on the metatarget for this systemtest
      if(NOT "${STATINFO___CONFIGS}" STREQUAL "__empty")
        add_dependencies(${STATVAR_BASENAME} ${tname})
      endif()

      # treat compile definitions
      foreach(cd ${STATINFO___STATIC_DATA})
        target_compile_definitions(${tname} PUBLIC "${cd}=${STATINFO_${conf}_${cd}}")
      endforeach()

      # maybe output debug information
      if(${STATVAR_DEBUG})
        message("Generated target ${tname}")
        get_property(cd TARGET ${tname} PROPERTY COMPILE_DEFINITIONS)
        message("  with COMPILE_DEFINITIONS: ${cd}")
      endif()

      # And append the target to the list of created targets
      list(APPEND targetlist "${tname}")
    endif()
    if(${STATVAR_DEBUG})
      message("Generating target ${tname} skipped because it already existed!")
    endif()
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

  # Allow absolute paths to the ini file
  if(NOT IS_ABSOLUTE ${TARGVAR_INIFILE})
    set(TARGVAR_INIFILE ${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE})
  endif()

  # set a default for the script. call_executable.py just calls the executable.
  # There, it is also possible to hook in things depending on the inifile
  if(NOT TARGVAR_SCRIPT)
    set(TARGVAR_SCRIPT dune_execute.py)
  endif()

  # Configure a bogus file from the meta ini file. This is a trick to retrigger configuration on meta ini changes.
  string(REPLACE "/" "_" BOGUSFILE "tmp_${TARGVAR_INIFILE}")
  configure_file(${TARGVAR_INIFILE} ${CMAKE_CURRENT_BINARY_DIR}/${BOGUSFILE})

  # expand the given meta ini file into the build tree
  dune_execute_process(COMMAND ${CMAKE_BINARY_DIR}/run-in-dune-env dune_expand_metaini.py
                               --cmake
                               --ini ${TARGVAR_INIFILE}
                               --dir ${CMAKE_CURRENT_BINARY_DIR}
                               --file ${CMAKE_CURRENT_BINARY_DIR}/interface.log
                       ERROR_MESSAGE "Error expanding ${TARGVAR_INIFILE}")

  parse_python_data(PREFIX iniinfo FILE ${CMAKE_CURRENT_BINARY_DIR}/interface.log)

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

      if(${DOSOMETHING})
        # Make sure to exclude the target from all, even when it is user-provided
        # This is exactly what dune_add_test does in dune-common
        get_target_property(aliased ${target} ALIASED_TARGET)
        if(NOT aliased)
          if(DUNE_BUILD_TESTS_ON_MAKE_ALL)
            set_property(TARGET ${target} PROPERTY EXCLUDE_FROM_ALL 0)
          else()
            set_property(TARGET ${target} PROPERTY EXCLUDE_FROM_ALL 1)
          endif()
        endif()

        # and have it depend on the metatarget build_tests, mimicking dune-common again
        add_dependencies(build_tests ${target})

        get_target_property(target_type ${target} TYPE)
        if (target_type STREQUAL "EXECUTABLE")
          set(EXEC_ARG --exec "$<TARGET_FILE_DIR:${target}>/$<TARGET_FILE_NAME:${target}>")
        endif ()

        # Now add the actual test!
        if(NOT ${MPI_CXX_FOUND})
          add_test(NAME ${target}_${ininame}
                    COMMAND ${CMAKE_BINARY_DIR}/run-in-dune-env ${TARGVAR_SCRIPT}
                    ${EXEC_ARG}
                    --ini "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}"
                    --source ${CMAKE_CURRENT_SOURCE_DIR}
                   )
        else()
          add_test(NAME ${target}_${ininame}
                    COMMAND ${CMAKE_BINARY_DIR}/run-in-dune-env ${TARGVAR_SCRIPT}
                    ${EXEC_ARG}
                    --ini "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}"
                    --source ${CMAKE_CURRENT_SOURCE_DIR}
                    --mpi-exec "${MPIEXEC}"
                    --mpi-numprocflag=${MPIEXEC_NUMPROC_FLAG}
                    --mpi-preflags "${MPIEXEC_PREFLAGS}"
                    --mpi-postflags "${MPIEXEC_POSTFLAGS}"
                    --max-processors=${DUNE_MAX_TEST_CORES}
                   )
        endif()
        set_property(TEST ${target}_${ininame} PROPERTY LABELS ${iniinfo_labels_${ininame}} DUNE_SYSTEMTEST)
        set_tests_properties(${target}_${ininame} PROPERTIES SKIP_RETURN_CODE 77)
      endif()
    endforeach()
  endforeach()
endfunction()

function(dune_add_system_test)
  # parse arguments
  set(OPTION DEBUG NO_TESTS)
  set(SINGLE INIFILE BASENAME SCRIPT)
  set(MULTI SOURCE TARGET CREATED_TARGETS)
  cmake_parse_arguments(SYSTEMTEST "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(SYSTEMTEST_UNPARSED_ARGUMENTS)
    message(WARNING "dune_add_system_test: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # construct a string containg DEBUG to pass the debug flag to the other macros
  set(DEBUG "")
  if(SYSTEMTEST_DEBUG)
    set(DEBUG "DEBUG")
  endif()

  # Allow absolute paths to the ini file
  if(NOT IS_ABSOLUTE ${SYSTEMTEST_INIFILE})
    set(SYSTEMTEST_INIFILE ${CMAKE_CURRENT_SOURCE_DIR}/${SYSTEMTEST_INIFILE})
  endif()

  # set a default for the script. call_executable.py just calls the executable.
  # There, it is also possible to hook in things depending on the inifile
  if(NOT SYSTEMTEST_SCRIPT)
    set(SYSTEMTEST_SCRIPT dune_execute.py)
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

    # If the NO_TESTS option is given, we discard the targetlist here
    # that will prohibit the addition of tests in the implementation of
    # add_system_test_per_target.
    if(SYSTEMTEST_NO_TESTS)
      set(targetlist)
    endif()

    add_system_test_per_target(INIFILE ${SYSTEMTEST_INIFILE}
                               TARGET ${targetlist}
                               SCRIPT ${SYSTEMTEST_SCRIPT}
                               ${DEBUG}
                               TARGETBASENAME ${SYSTEMTEST_BASENAME})
  else()
    dune_execute_process(COMMAND ${CMAKE_BINARY_DIR}/run-in-dune-env dune_has_static_section.py
                                 --ini ${SYSTEMTEST_INIFILE}
                         RESULT_VARIABLE res
                         ERROR_MESSAGE "Error checking for static info in ${SYSTEMTEST_INIFILE}")
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
