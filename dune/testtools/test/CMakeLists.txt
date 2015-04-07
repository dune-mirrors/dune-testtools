set(TESTPROGS outputtreetest triggertest)

add_subdirectory(constructiontest)
add_subdirectory(cmakepython)
add_subdirectory(staticvariants)
add_subdirectory(dynamicvariants)
add_subdirectory(allvariants)

add_executable("outputtreetest" outputtreetest.cc)

include(ConditionalIncludes)
add_executable("triggertest" triggertest.cc)
set_property(TARGET triggertest APPEND PROPERTY COMPILE_DEFINITIONS SWITCH1)
resolve_conditional_includes(triggertest "SWITCH1;SWITCH2")

foreach(_exe ${TESTPROGS})
  target_link_libraries(${_exe} ${DUNE_LIBS})
  add_test(${_exe} ${_exe})
endforeach(_exe ${TESTPROGS})

add_dune_convergence_test(SOURCE test_convergencetest.cc INIFILE test_convergencetest.ini BASENAME convergence_test OUTPUT_TARGETS targetlist)
foreach(_exe ${targetlist})
  list(APPEND TESTPROGS ${_exe})
  target_link_libraries(${_exe} ${DUNE_LIBS})
endforeach(_exe ${targetlist})

add_directory_test_target(_test_target)
add_dependencies(${_test_target} ${TESTPROGS})
