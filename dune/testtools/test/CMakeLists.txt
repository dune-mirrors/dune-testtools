set(TESTPROGS outputtreetest triggertest)

add_subdirectory(constructiontest)
add_subdirectory(cmakepython)
add_subdirectory(staticvariants)
add_subdirectory(dynamicvariants)
add_subdirectory(onemacrodynamicvariants)
add_subdirectory(allvariants)
add_subdirectory(parallel)
add_subdirectory(convergencetest)

add_executable("outputtreetest" outputtreetest.cc)

include(ConditionalIncludes)
add_executable("triggertest" triggertest.cc)
set_property(TARGET triggertest APPEND PROPERTY COMPILE_DEFINITIONS SWITCH1)
resolve_conditional_includes(triggertest "SWITCH1;SWITCH2")

foreach(_exe ${TESTPROGS})
  target_link_libraries(${_exe} ${DUNE_LIBS})
  add_test(${_exe} ${_exe})
endforeach()

add_directory_test_target(_test_target)
add_dependencies(${_test_target} ${TESTPROGS})
