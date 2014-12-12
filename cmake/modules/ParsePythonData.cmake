# A CMake module defining macros to parse data from python scripts
#
# parse_python_data(prefix input)
#
# The <prefix> will be used for the variables. For each <key> in the data,
# a variable <prefix>_<key> will be available in the scope of the call.
# input: The string coming from the python output. Note, that it has to be
# put in double quotes.

function(parse_python_data prefix input)
  # these keys are an agreement between the python and the cmake module
  # they can be changed to whatever keys, as long as they are updated on
  # both ends.
  set(MULTIKEYS __SINGLE __MULTI __DATA)

  # first parsing: What keys are present in the data
  cmake_parse_arguments(KEYS "" "" "${MULTIKEYS}" ${input})

  # second parsing: What data is associated with the keys
  cmake_parse_arguments(${prefix} "" "${KEYS___SINGLE}" "${KEYS___MULTI}" ${KEYS___DATA})

  # set the variables in the parent scope!
  # Note: Having this function as a macro would inline it into the outer
  # scope and thus setting all variables correctly - but also the temporary
  # ones from this script. Especially w.r.t. to multiple calls of this macro
  # that should be avoided!
  foreach(key in ${KEYS___SINGLE} ${KEYS___MULTI})
    set(${prefix}_${key} ${${prefix}_${key}} PARENT_SCOPE)
  endforeach(key in ${KEYS___SINGLE} ${KEYS___MULTI})

endfunction(parse_python_data prefix inputstr)
