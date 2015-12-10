# Macros to just expand an inifile into the build tree
# without adding any systemtests.
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

function(dune_expand_metaini)
  # parse arguments
  set(OPTION DEBUG NO_STATIC)
  set(SINGLE INIFILE BASENAME)
  set(MULTI SOURCE CREATED_TARGETS)
  cmake_parse_arguments(EXPAND "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})

  if(EXPAND_UNPARSED_ARGUMENTS)
    message(WARNING "dune_expand_metaini: Encountered unparsed arguments: This often indicates typos in named arguments")
  endif()

  # construct a string containg DEBUG to pass the debug flag to the other macros
  set(DEBUG "")
  if(EXPAND_DEBUG)
    set(DEBUG "DEBUG")
  endif()

  if(EXPAND_NO_STATIC)
    add_system_test_per_target(INIFILE ${EXPAND_INIFILE}
                               ${DEBUG}
                              )
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
