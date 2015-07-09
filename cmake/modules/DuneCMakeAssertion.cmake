# Implement configure time assertions to test cmake modules.
#
# dune_assert(MESSAGE message
#            [COND condition]
#            [TEST_EXISTS name]
#            [LIST_LENGTH list length]
#            [WARNING]
# )
# 
# Fail with a fatal error if the given condition evaluates to false.
# (or with a warning if WARNING has been given). The condition might either
# be given through COND, which accpets anything the if statement accepts
# or through one of the following shortcuts:
# * TEST_EXISTS true if a test of the given name has been added
# * LIST_LENGTH true if the given list has the given length
#
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
  # If we got so far, we should just evaluate the givne if statement.
  if(NOT ${ASSERT_COND})
    fail_assert(${ASSERT_MESSAGE} ${ASSERT_WARNING})
    return()
  endif()
endfunction()
