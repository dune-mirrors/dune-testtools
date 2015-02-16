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
#                            INIFILE inifile
#                            [TARGETBASENAME basename])
#
# For a preconfigured set of targets, test targets are created. The inifile
# for the test is expanded into the build tree. The number of tests is
# the product of the number of executable targets and inifiles defined by
# the metainifile. The same meta inifile is used for all targets. Call
# multiple times for different behaviour. The TARGETBASENAME parameter is
# used internally, to check whether an ini file is matching a given executable.
#
# add_dune_system_test(TARGET target)

find_package(PythonInterp)

include(ParsePythonData)
include(AddFolderLinkOrCopy)

function(add_static_variants)
  # parse the parameter list
  set(OPTION DEBUG)
  set(SINGLE BASENAME INIFILE TARGETS)
  set(MULTI SOURCE)
  cmake_parse_arguments(STATVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  # get the static information from the ini file
  # TODO maybe check whether an absolute path has been given for a mini file
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${DUNE_TESTTOOLS_PATH}/python/static_metaini.py --ini ${CMAKE_CURRENT_SOURCE_DIR}/${STATVAR_INIFILE}
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
  set(SINGLE INIFILE TARGETBASENAME)
  set(MULTI TARGET)
  cmake_parse_arguments(TARGVAR "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  # expand the given meta ini file into the build tree
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${DUNE_TESTTOOLS_PATH}/python/metaIni.py --ini ${CMAKE_CURRENT_SOURCE_DIR}/${TARGVAR_INIFILE} --dir ${CMAKE_CURRENT_BINARY_DIR}
                  OUTPUT_VARIABLE output)

  parse_python_data(PREFIX iniinfo INPUT "${output}")

  # add the tests for all targets
  foreach(target ${TARGVAR_TARGET})
    foreach(inifile ${iniinfo_names})
      if (${TARGVAR_DEBUG})
        message("  Adding a target with executable ${target} and inifile ${inifile}...")
      endif (${TARGVAR_DEBUG})

      # Somehow the test have to be named, although the naming scheme is not relevant for
      # the selection of tests to run on the server side. For the moment we combine the
      # executable target name with the ini file name.
      get_filename_component(ininame ${inifile} NAME_WE)

      # check whether something needs to be done. This is either when our target is matching
      # the given suffix, or when TARGETBASENAME isnt given (this indicates stand-alone usage)
      set(DOSOMETHING FALSE)
      if("${TARGVAR_TARGETBASENAME}_${iniinfo_${inifile}_suffix}" STREQUAL "${target}")
        set(DOSOMETHING TRUE)
      endif("${TARGVAR_TARGETBASENAME}_${iniinfo_${inifile}_suffix}" STREQUAL "${target}")
      if(NOT DEFINED TARGVAR_TARGETBASENAME)
        set(DOSOMETHING TRUE)
      endif(NOT DEFINED TARGVAR_TARGETBASENAME)

      if (${TARGVAR_DEBUG})
        message("${DOSOMETHING}")
      endif (${TARGVAR_DEBUG})

      if (${TARGVAR_DEBUG} AND ${DOSOMETHING})
        message("---> Adding a test with executable ${target} and inifile ${inifile}...")
      endif (${TARGVAR_DEBUG} AND ${DOSOMETHING})

      # get the extension of the ini file (can be user defined)
      get_filename_component(iniext ${inifile} EXT)

      if(${DOSOMETHING})
        if("${iniinfo_${inifile}_optionkey}" STREQUAL "")
          add_test(${target}_${ininame} ${target} "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}")
        else("${iniinfo_${inifile}_optionkey}" STREQUAL "")
          add_test(${target}_${ininame} ${target} ${iniinfo_${inifile}_optionkey} "${CMAKE_CURRENT_BINARY_DIR}/${ininame}${iniext}")
        endif("${iniinfo_${inifile}_optionkey}" STREQUAL "")
      endif(${DOSOMETHING})
    endforeach(inifile ${iniinfo_names})
  endforeach(target ${TARGVAR_TARGET})

  # in case of user provided external grid files (have to be in a "grids" folder in the
  # source dir) copy the grids folder
  add_folder_copy(grids)

endfunction(add_system_test_per_target)

function(add_dune_system_test)
  # parse arguments
  set(OPTION DEBUG)
  set(SINGLE INIFILE BASENAME)
  set(MULTI SOURCE LIBRARIES)
  cmake_parse_arguments(SYSTEMTEST "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  # construct a string containg DEBUG to pass the debug flag to the other macros
  set(DEBUG "")
  if (${SYSTEMTEST_DEBUG})
    set(DEBUG "DEBUG")
  endif (${SYSTEMTEST_DEBUG})

  # The above macros have been written in a way that allows us to use them
  # combined. The TARGETBASENAME parameter is introduced for that.

  add_static_variants(SOURCE ${SYSTEMTEST_SOURCE}
                      BASENAME ${SYSTEMTEST_BASENAME}
                      INIFILE ${SYSTEMTEST_INIFILE}
                      TARGETS targetlist
                      ${DEBUG})

  # link the given libraries to all targets in this systemtest
  if (${DEBUG})
    message("linking libraries...")
  endif (${DEBUG})
  # TODO maybe it is possible to specify libraries for specific tests within a systemtest
  foreach(_target ${targetlist})
    # always add the DUNE libaries
    target_link_libraries(${_target} ${DUNE_LIBS})
    if (${DEBUG})
      message("  linked the target ${_target} to the DUNE libraries")
    endif (${DEBUG})
    # link user specific libraries (partly reusing the dune macros)
    foreach(_library ${SYSTEMTEST_LIBRARIES})
      if(${_library} STREQUAL "all")
        # add all libraries, convinience keyword for test using a lot of the predefined library macros
        add_dune_all_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to all libraries (add_dune_all_flags)")
        endif (${DEBUG})
      elseif(${_library} STREQUAL "mpi")
        add_dune_mpi_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to the MPI libraries")
        endif (${DEBUG})
      elseif(${_library} STREQUAL "alugrid")
        add_dune_alugrid_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to the ALUGrid libraries")
        endif (${DEBUG})
      elseif(${_library} STREQUAL "parmetis")
        add_dune_parmetis_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to the ParMETIS libraries")
        endif (${DEBUG})
      elseif(${_library} STREQUAL "ug")
        add_dune_ug_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to the UG libraries")
        endif (${DEBUG})
      elseif(${_library} STREQUAL "umfpack")
        add_dune_umfpack_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to the UMFPack libraries")
        endif (${DEBUG})
      elseif(${_library} STREQUAL "superlu")
        add_dune_superlu_flags(${_target})
        if (${DEBUG})
          message("  linked the target ${_target} to the SuperLU libraries")
        endif (${DEBUG})
      else(${_library} STREQUAL "all")
        # libaries not without dune macro
        target_link_libraries(${_target} ${_library})
        if (${DEBUG})
          message("  linked the target ${_target} to ${_library}")
        endif (${DEBUG})
      endif(${_library} STREQUAL "all")
    endforeach(_library ${SYSTEMTEST_LIBRARIES})
  endforeach(_target ${targetlist})

  add_system_test_per_target(INIFILE ${SYSTEMTEST_INIFILE}
                             TARGET ${targetlist}
                             ${DEBUG}
                             TARGETBASENAME ${SYSTEMTEST_BASENAME})

endfunction(add_dune_system_test)
