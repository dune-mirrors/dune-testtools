add_dune_convergence_test(SOURCE test_convergencetest.cc INIFILE test_convergencetest.ini BASENAME convergence_test OUTPUT_TARGETS targetlist ${DEBUG_MACRO_TESTS})

foreach(_exe ${targetlist})
  target_link_libraries(${_exe} ${DUNE_LIBS})
endforeach()
