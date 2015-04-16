if(${DEBUG_MACRO_TESTS})
  message("Performing tests for the macro add_dune_system_test:")
  add_dune_system_test(SOURCE source.cc BASENAME allvariants INIFILE test.mini DEBUG)
else()
  add_dune_system_test(SOURCE source.cc BASENAME allvariants INIFILE test.mini)
endif()

