set(TESTPROGS outputtreetest constructiontest)

add_directory_test_target(_test_target)
add_dependencies(${_test_target} ${TESTPROGS})

add_executable("outputtreetest" outputtreetest.cc)
add_executable("constructiontest" constructiontest.cc)
add_dune_ug_flags(constructiontest)

foreach(_exe ${TESTPROGS})
  target_link_libraries(${_exe} ${DUNE_LIBS})
  add_test(${_exe} ${_exe})
endforeach(_exe ${TESTPROGS})
