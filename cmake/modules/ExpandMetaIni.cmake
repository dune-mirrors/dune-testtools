# Macros to just expand an inifile into the build tree
# without adding any systemtests.
#
# .. cmake_function:: dune_expand_metaini_nostatic
#
#    .. cmake_param:: INIFILE
#       :single:
#       :required:
#
#       The inifile to expand into the build tree.
#
#    Expand a meta ini file into the buildtree. This function does not
#    create any system tests, but just expands the meta ini file.
#    It does not consider static variants, see :ref:`dune_expand_metaini`
#    for that.
#
# .. cmake_function:: dune_expand_metaini
#
#    .. cmake_param:: INIFILE
#       :single:
#       :required:
#
#       The inifile to expand into the build tree.
#
#    .. cmake_param:: NO_STATIC
#       :option:
#
#       Set to treat static information just as any other.
#
#    .. cmake_param:: BASENAME
#       :single:
#
#       The basename for the executables, can be omitted
#       if the NO_STATIC option is set.
#
#    .. cmake_param:: SOURCE
#       :multi:
#
#       The source file to build executables from, can be omitted
#       if the NO_STATIC option is set.
#
#    .. cmake_param:: CREATED_TARGETS
#       :single:
#
#       The list of targets that were created by this function.
#
#    .. cmake_param:: DEBUG
#       :option:
#
#       Enable some debugging output.
#
#    Expand a meta ini file into the buildtree. Also consider static
#    variants, unless :code:`NO_STATIC` has been given. For more details
#    on all the other parameters, see :ref:`dune_add_system_test`.
#

function(dune_expand_metaini_nostatic)
  set(OPTION "")
  set(SINGLE INIFILE BASENAME)
  set(MULTI "")
  cmake_parse_arguments(EXPAND "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})
  if(EXPAND_UNPARSED_ARGUMENTS)
    message(WARNING "dune_expand_metaini_nostatic: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  if(NOT EXPAND_INIFILE)
    message(FATAL_ERROR "The INIFILE parameter is required for function dune_expand_metaini_nostatic")
  endif()

  # Allow absolute paths to the ini file
  if(NOT IS_ABSOLUTE ${EXPAND_INIFILE})
    set(EXPAND_INIFILE ${CMAKE_CURRENT_SOURCE_DIR}/${EXPAND_INIFILE})
  endif()

  # Configure a bogus file from the meta ini file. This is a trick to retrigger configuration on meta ini changes.
  string(REPLACE "/" "_" BOGUSFILE "tmp_${EXPAND_INIFILE}")
  configure_file(${EXPAND_INIFILE} ${CMAKE_CURRENT_BINARY_DIR}/${BOGUSFILE})

  # expand the given meta ini file into the build tree
  dune_execute_process(COMMAND ${CMAKE_BINARY_DIR}/run-in-dune-env dune_expand_metaini.py
                               --cmake
                               --ini ${EXPAND_INIFILE}
                               --dir ${CMAKE_CURRENT_BINARY_DIR}
                               --file ${CMAKE_CURRENT_BINARY_DIR}/interface.log
                       ERROR_MESSAGE "Error expanding ${EXPAND_INIFILE}")
endfunction()

function(dune_expand_metaini)
  # parse arguments
  set(OPTION DEBUG NO_STATIC)
  set(SINGLE INIFILE BASENAME)
  set(MULTI SOURCE CREATED_TARGETS)
  cmake_parse_arguments(EXPAND "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(EXPAND_UNPARSED_ARGUMENTS)
    message(WARNING "dune_expand_metaini: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  if(NOT EXPAND_INIFILE)
    message(FATAL_ERROR "The INIFILE parameter is required for function dune_expand_metaini")
  endif()

  # construct a string containg DEBUG to pass the debug flag to the other macros
  set(DEBUG "")
  if(EXPAND_DEBUG)
    set(DEBUG "DEBUG")
  endif()

  if(EXPAND_NO_STATIC)
    dune_expand_metaini_nostatic(INIFILE ${EXPAND_INIFILE})
  else()
    dune_add_system_test(INIFILE ${EXPAND_INIFILE}
                         SOURCE ${EXPAND_SOURCE}
                         CREATED_TARGETS output
                         BASENAME ${EXPAND_BASENAME}
                         ${DEBUG}
                         NO_TESTS
                        )
    set(${EXPAND_CREATED_TARGETS} ${output} PARENT_SCOPE)
  endif()

endfunction()
