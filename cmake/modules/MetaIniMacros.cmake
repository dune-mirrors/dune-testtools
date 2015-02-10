# This module offers macros to treat meta ini files as part of the source
# tree of a project
#
# expand_meta_ini(METAFILE <file>
#                 RETURNSTR <var>
#                )
# 
# The metafile <file> is expected to be in the source and will be expanded to the
# build directory (upon configure time). The return value of the script is written
# into the variable <var>.

function(expand_meta_ini)
  # set the variable controling cmake parse arguments and parse the function call
  set(options)
  set(oneValueArgs METAFILE RETURNSTR)
  set(multiValueArgs)
  cmake_parse_arguments(EXPANDER "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN} )

  # check for the python interpreter to be in place
  if(NOT PYTHONINTERP_FOUND)
    message(FATAL_ERROR "Tried using python without a python interpreter found.")
  endif(NOT PYTHONINTERP_FOUND)

  # call the python script doing a meta ini expanding
  execute_process(COMMAND ${PYTHON_EXECUTABLE} "${DUNE_TESTTOOLS_PATH}/python/exec_metaini.py" "${CMAKE_CURRENT_SOURCE_DIR}/${EXPANDER_METAFILE}"
                  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                  OUTPUT_VARIABLE expander_output
                 )

  # set the output variable in the outer scope
  set(${EXPANDER_RETURNSTR} ${expander_output} PARENT_SCOPE)
endfunction(expand_meta_ini)
