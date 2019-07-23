# This is a configure test for the Python CMake interface

execute_process(COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/testdata.py ${CMAKE_CURRENT_BINARY_DIR}/interface.log
                )

include(ParsePythonData)
parse_python_data(PREFIX TESTPREFIX FILE ${CMAKE_CURRENT_BINARY_DIR}/interface.log)

if(NOT ${TESTPREFIX_3} EQUAL "5")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_3 not parsed correctly")
endif()

if(NOT ${TESTPREFIX_2} EQUAL "17")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_2 not parsed correctly")
endif()

if(NOT ${TESTPREFIX_8} EQUAL "2;4;something")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_8 not parsed correctly")
endif()

if(NOT ${TESTPREFIX_mykey} EQUAL "bla;blubb")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_mykey not parsed correctly")
endif()

if(NOT ${TESTPREFIX_nested_bla} EQUAL "val")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_nested_bla not parsed correctly")
endif()

if(NOT ${TESTPREFIX_nested_5_deeper} EQUAL "wow!")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_nested_5_deeper not parsed correctly")
endif()

if(${DEBUG_MACRO_TESTS})
  message("All configure tests for the Python CMake interface have been run...")
endif()
