foreach(var CONVERGENCE_TEST_INIS CONVERGENCE_TEST_ID CONVERGENCE_TEST_META_INI CONVERGENCE_TEST_TARGET CONVERGENCE_TEST_SCRIPT)
  if(NOT DEFINED ${var})
    message(FATAL_ERROR "'${var}' must be defined on the command line")
  endif()
endforeach()

string(REPLACE "+" ";" inis ${CONVERGENCE_TEST_INIS})

foreach(ini ${inis})
  # Execute the test-executable
  set(ENV{PYTHONPATH} "${DUNE_TESTTOOLS_PATH}/python:$ENV{PYTHONPATH}")
  get_filename_component(module ${CONVERGENCE_TEST_SCRIPT} NAME_WE)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -m dune_testtools.wrapper.${module} --exec ${CONVERGENCE_TEST_TARGET} --ini ${ini}
                  RESULT_VARIABLE result ERROR_VARIABLE err_output OUTPUT_VARIABLE output)

  message(STATUS "${err_output}")
  # Check its return status
  if(result)
    message(FATAL_ERROR "Test run with ${CONVERGENCE_TEST_TARGET} and inifile ${ini} failed")
  endif()
endforeach()

# run the evaluation script
set(ENV{PYTHONPATH} "${DUNE_TESTTOOLS_PATH}/python:$ENV{PYTHONPATH}")
execute_process(COMMAND ${PYTHON_EXECUTABLE} -m dune_testtools.wrapper.test_convergence --ini ${CONVERGENCE_TEST_META_INI} --test ${CONVERGENCE_TEST_ID}
                  RESULT_VARIABLE result ERROR_VARIABLE output OUTPUT_VARIABLE output)

# Check its return status
if(result)
  message(SEND_ERROR "${output}")
  message(FATAL_ERROR "Test run with ${CONVERGENCE_TEST_TARGET} and inifile ${ini} failed")
endif()
