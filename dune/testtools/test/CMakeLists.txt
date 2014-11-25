set(TESTPROGS outputtreetest)

add_directory_test_target(_test_target)
add_dependencies(${_test_target} ${TESTPROGS})

add_executable("outputtreetest" outputtreetest.cc)

foreach(_exe ${TESTPROGS})
  target_link_libraries(${_exe} "dunecommon")
  add_test(${_exe} ${_exe})
endforeach(_exe ${TESTPROGS})