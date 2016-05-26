# A CMake module defining the interface to read data from Python
#
# .. cmake_function:: parse_python_data
#
#    .. cmake_param:: PREFIX
#       :single:
#       :required:
#
#       The prefix to give to the CMake variables.
#
#    .. cmake_param:: INPUT
#       :single:
#       :required:
#
#       The input string, which is the stdout of a Python script
#       that used the :code:`printForCMake` function from :code:`dune.testtools`
#
#    The function that implements the data interface between Python and
#    CMake from the CMake side.
#
#    .. note::
#       This is intended for internal use only.
#

function(parse_python_data)
  set(SINGLE PREFIX)
  set(MULTI INPUT)
  cmake_parse_arguments(PYPARSE "" "${SINGLE}" "${MULTI}" ${ARGN})
  # these keys are an agreement between the Python and the CMake module
  # they can be changed to whatever keys, as long as they are updated on
  # both ends.
  set(SINGLEKEY __SEMICOLON)
  set(MULTIKEYS __SINGLE __MULTI __DATA)
  # first parsing: What keys are present in the data
  cmake_parse_arguments(KEYS "" "${SINGLEKEY}" "${MULTIKEYS}" ${PYPARSE_INPUT})

  # second parsing: What data is associated with the keys
  cmake_parse_arguments(DATA "" "${KEYS___SINGLE}" "${KEYS___MULTI}" ${KEYS___DATA})

  # set the variables in the parent scope!
  # Note: Having this function as a macro would inline it into the outer
  # scope and thus setting all variables correctly - but also the temporary
  # ones from this script. Especially w.r.t. to multiple calls of this macro
  # that should be avoided!
  foreach(key ${KEYS___SINGLE} ${KEYS___MULTI})
    # restore any semicolons in the data
    string(REPLACE "${KEYS___SEMICOLON}" ";" output "${DATA_${key}}")
    set(${PYPARSE_PREFIX}_${key} ${output} PARENT_SCOPE)
  endforeach()
endfunction()
