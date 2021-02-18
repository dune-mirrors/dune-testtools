dune_add_system_test(SOURCE test_convergencetest.cc
                     INIFILE test_convergencetest.ini
                     BASENAME convergence_test
                     CREATED_TARGETS targetlist
                     SCRIPT dune_convergencetest.py
                     ${DEBUG_MACRO_TESTS})

dune_add_system_test(SOURCE test_system_convergencetest.cc
                     INIFILE test_system_convergencetest.ini
                     BASENAME system_convergence_test
                     CREATED_TARGETS targetlist2
                     SCRIPT dune_convergencetest.py
                     ${DEBUG_MACRO_TESTS})


foreach(_exe ${targetlist} ${targetlist2})
  target_link_libraries(${_exe} ${DUNE_LIBS})
endforeach()
