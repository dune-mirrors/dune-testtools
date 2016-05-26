# Implement configure time assertions to test CMake modules.
#
# .. cmake_function:: dune_assert
#
#    .. cmake_param:: MESSAGE
#       :single:
#       :required:
#
#       The message to print if the assertion fails.
#
#    .. cmake_param:: COND
#       :single:
#
#       A condition that may be evaluated by the CMake command :code:`if`.
#
#    .. cmake_param:: TEST_EXISTS
#       :single:
#       :argname: name
#
#       A special condition, that tests whether a test of the
#       given name has been added to CMake. Note that such check
#       does not exist in CMake. To work around this, the existence
#       of a test label is checked. This works fine for us, because
#       the functions in DuneSystemtests apply at least one
#       label to all generated tests. It might fail for arbitrary tests
#       though.
#
#    .. cmake_param:: LIST_LENGTH
#       :single:
#       :argname: list length
#
#       A special condition to check whether the length of a given list
#       equals the expected length.
#
#    .. cmake_param:: WARNING
#       :option:
#
#       If given, a failed assertion only throws a warning instead of an error.
#
#    Implement configure time assertions in CMake. This may be used to write
#    unit tests for CMake functions. Any condition that can be evaluated by
#    CMake's command :code:`if` may be used. Some additional conditions are
#    implemented, check below documentation for details. Only one conditions
#    should be given. Giving more than one, will result in all but one being
#    ignored.
#

macro(fail_assert message warning)
  if(warning)
    message(WARNING ${message})
  else()
    message(FATAL_ERROR ${message})
  endif()
endmacro()

function(dune_assert)
  set(OPTION WARNING)
  set(SINGLE MESSAGE TEST_EXISTS)
  set(MULTI COND LIST_LENGTH)
  cmake_parse_arguments(ASSERT "${OPTION}" "${SINGLE}" "${MULTI}" ${ARGN})
  if(ASSERT_TEST_EXISTS)
    # Provide a workaround to test whether a test of a given name exists in the project
    # The workaround relies on the DUNE_SYSTEMTEST labelling being set on all of our tests.
    get_test_property(${ASSERT_TEST_EXISTS} LABELS result)
    if(NOT result)
      fail_assert(${ASSERT_MESSAGE} ${ASSERT_WARNING})
    endif()
    return()
  endif()
  if(ASSERT_LIST_LENGTH)
    list(GET ASSERT_LIST_LENGTH 0 name)
    list(GET ASSERT_LIST_LENGTH 1 len)
    list(LENGTH ${name} result)
    if(NOT ${result} EQUAL ${len})
      fail_assert(${ASSERT_MESSAGE} ${ASSERT_WARNING})
    endif()
    return()
  endif()
  # If we got so far, we should just evaluate the given if statement.
  if(NOT ${ASSERT_COND})
    fail_assert(${ASSERT_MESSAGE} ${ASSERT_WARNING})
    return()
  endif()
endfunction()
