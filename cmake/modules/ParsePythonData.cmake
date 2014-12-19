# A CMake module defining macros to parse data from python scripts
#
# parse_python_data(PREFIX prefix
#                   INPUT input
#                  )
#
# The <prefix> will be used for the variables. For each <key> in the data,
# a variable <prefix>_<key> will be available in the scope of the call.
# input: The string coming from the python output. Note, that it has to be
# put in double quotes.

function(parse_python_data)
  set(SINGLE PREFIX)
  set(MULTI INPUT)
  cmake_parse_arguments(PYPARSE "" "${SINGLE}" "${MULTI}" ${ARGN})
  # these keys are an agreement between the python and the cmake module
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
  endforeach(key ${KEYS___SINGLE} ${KEYS___MULTI})
endfunction(parse_python_data)
