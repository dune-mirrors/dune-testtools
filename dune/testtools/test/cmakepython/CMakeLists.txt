# This is a configure test for the Python CMake interface

execute_process(COMMAND PYTHONPATH=.:PYTHONPATH {PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/testdata.py
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/python
                OUTPUT_VARIABLE data
)

include(ParsePythonData)
parse_python_data(PREFIX TESTPREFIX INPUT ${data})

if(NOT ${TESTPREFIX_3} EQUAL "5")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_3 not parsed correctly")
endif(NOT ${TESTPREFIX_3} EQUAL "5")

if(NOT ${TESTPREFIX_2} EQUAL "17")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_2 not parsed correctly")
endif(NOT ${TESTPREFIX_2} EQUAL "17")

if(NOT ${TESTPREFIX_8} EQUAL "2;4;something")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_8 not parsed correctly")
endif(NOT ${TESTPREFIX_8} EQUAL "2;4;something")

if(NOT ${TESTPREFIX_MYKEY} EQUAL "bla;blubb")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_MYKEY not parsed correctly")
endif(NOT ${TESTPREFIX_MYKEY} EQUAL "bla;blubb")

if(NOT ${TESTPREFIX_NESTED_BLA} EQUAL "val")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_NESTED_BLA not parsed correctly")
endif(NOT ${TESTPREFIX_NESTED_BLA} EQUAL "val")

if(NOT ${TESTPREFIX_NESTED_5_DEEPER} EQUAL "wow!")
  message(FATAL_ERROR "Fatal error in Pyhton - CMake interface! TESTPREFIX_NESTED_5_DEEPER not parsed correctly")
endif(NOT ${TESTPREFIX_NESTED_5_DEEPER} EQUAL "wow!")

message("All configure tests for the Python CMake interface have been run...")