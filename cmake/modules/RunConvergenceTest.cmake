foreach(var CONVERGENCE_TEST_INIS CONVERGENCE_TEST_TARGET CONVERGENCE_TEST_SCRIPT)
  if(NOT DEFINED ${var})
    message(FATAL_ERROR "'${var}' must be defined on the command line")
  endif(NOT DEFINED ${var})
endforeach(var CONVERGENCE_TEST_INIS CONVERGENCE_TEST_TARGET CONVERGENCE_TEST_SCRIPT)

string(REPLACE "+" ";" inis ${CONVERGENCE_TEST_INIS})

foreach(ini ${inis})
  # Execute the test-executable
  set(ENV{PYTHONPATH} "${DUNE_TESTTOOLS_PATH}/python:$ENV{PYTHONPATH}")
  message(STATUS "$ENV{PYTHONPATH}")
  message(STATUS "PYTHON_EXECUTABLE: ${PYTHON_EXECUTABLE}")
  message(STATUS "COMMAND: ${PYTHON_EXECUTABLE} ${CONVERGENCE_TEST_SCRIPT} --exec ${CONVERGENCE_TEST_TARGET} --ini ${ini}")
  execute_process(COMMAND ${PYTHON_EXECUTABLE} ${CONVERGENCE_TEST_SCRIPT} --exec ${CONVERGENCE_TEST_TARGET} --ini ${ini}
                  RESULT_VARIABLE result ERROR_VARIABLE output OUTPUT_VARIABLE output)

  message(STATUS "${output}")
  # Check its return status
  if(result)
    message(FATAL_ERROR "Test run with ${CONVERGENCE_TEST_TARGET} and inifile ${ini} failed")
  endif(result)
endforeach(ini ${inis})