# This module offers macros to treat meta ini files as part of the source
# tree of a project
#
# expand_meta_ini(metafile)
# 
# The metafile is expected to be in the source and will be expanded to the 
# build directory (upon configure time)

function(expand_meta_ini metafile)
  if(NOT PYTHONINTERP_FOUND)
    message(FATAL_ERROR "Tried using python without a python interpreter found.")
  endif(NOT PYTHONINTERP_FOUND)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_SOURCE_DIR}/python/exec_metaini.py" "${CMAKE_CURRENT_SOURCE_DIR}/${metafile}"
                  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                 )
endfunction(expand_meta_ini)
