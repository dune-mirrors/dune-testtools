dune_add_system_test(SOURCE test_convergencetest.cc
                     INIFILE test_convergencetest.ini
                     BASENAME convergence_test
                     CREATED_TARGETS targetlist
                     SCRIPT dune_convergencetest.py
                     ${DEBUG_MACRO_TESTS})

foreach(_exe ${targetlist})
  target_link_libraries(${_exe} ${DUNE_LIBS})
endforeach()
