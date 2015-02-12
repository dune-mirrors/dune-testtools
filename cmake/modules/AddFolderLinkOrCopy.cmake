# Creates a symbolic link to the specified folder in the build directory
# ATTENTION: symbolic links are not supported by all file systems, e. g.
# it will not work on Windows.
#
# Arguments:
# - folder_name:                  name of the folder
#
macro(add_folder_link folder_name)
  # if present, add link to folder
  set(folder ${CMAKE_CURRENT_SOURCE_DIR}/${folder_name})
  if(EXISTS ${folder} AND IS_DIRECTORY ${folder})
    execute_process(
      COMMAND cmake -E create_symlink ${folder} ${CMAKE_CURRENT_BINARY_DIR}/${folder_name})
  endif()
endmacro()


# Creates a copy of the specified folder in the build directory
#
# Arguments:
# - folder_name:                  name of the folder
#
macro(add_folder_copy folder_name)
  # if present, copy folder
  set(folder ${CMAKE_CURRENT_SOURCE_DIR}/${folder_name})
  if(EXISTS ${folder} AND IS_DIRECTORY ${folder})
    file(COPY ${folder} DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
  endif()
endmacro()
