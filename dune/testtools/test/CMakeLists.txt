set(TESTPROGS outputtreetest constructiontest triggertest)

add_directory_test_target(_test_target)
add_dependencies(${_test_target} ${TESTPROGS})

add_executable("outputtreetest" outputtreetest.cc)
add_executable("constructiontest" constructiontest.cc)
add_dune_ug_flags(constructiontest)

add_executable("triggertest" triggertest.cc)
set_property(TARGET triggertest APPEND PROPERTY COMPILE_DEFINITIONS SWITCH1)
resolve_conditional_includes(triggertest "SWITCH1;SWITCH2")

foreach(_exe ${TESTPROGS})
  target_link_libraries(${_exe} ${DUNE_LIBS})
  add_test(${_exe} ${_exe})
endforeach(_exe ${TESTPROGS})
