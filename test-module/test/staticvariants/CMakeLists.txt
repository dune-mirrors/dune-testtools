add_static_variants(SOURCE source.cc INIFILE statictest.mini BASENAME statictest CREATED_TARGETS targetlist ${DEBUG_MACRO_TESTS})
dune_assert(COND TARGET statictest_1 MESSAGE "statictest: A target named statictest_1 should have been generated")
dune_assert(COND TARGET statictest_2 MESSAGE "statictest: A target named statictest_2 should have been generated")
dune_assert(LIST_LENGTH targetlist 2 MESSAGE "statictest: Two executables should have been generated")