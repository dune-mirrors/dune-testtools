if(dune-grid_FOUND)
  dune_add_system_test(SOURCE source.cc
                       INIFILE config.mini
                       BASENAME mysystemtest)
endif()
