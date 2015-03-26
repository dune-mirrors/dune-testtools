if(${DEBUG_MACRO_TESTS})
  message("Performing tests for the macro add_dune_system_test:")
  add_dune_system_test(SOURCE source.cc BASENAME test INIFILE test.mini DEBUG)
else(${DEBUG_MACRO_TESTS})
  add_dune_system_test(SOURCE source.cc BASENAME test INIFILE test.mini)
endif(${DEBUG_MACRO_TESTS})

