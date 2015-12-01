dune_add_system_test(SOURCE source.cc BASENAME allvariants INIFILE test.mini CREATED_TARGETS output ${DEBUG_MACRO_TESTS})

dune_assert(COND TARGET allvariants_1 MESSAGE "allvariants: A target named allvariants_1 should have been generated")
dune_assert(COND TARGET allvariants_2 MESSAGE "allvariants: A target named allvariants_2 should have been generated")
dune_assert(LIST_LENGTH output 2 MESSAGE "allvariants: Two executables should have been generated")
dune_assert(TEST_EXISTS allvariants_1_0000 MESSAGE "allvariants: A test called allvariants_1_0000 should exist")
dune_assert(TEST_EXISTS allvariants_1_0001 MESSAGE "allvariants: A test called allvariants_1_0001 should exist")
dune_assert(TEST_EXISTS allvariants_2_0002 MESSAGE "allvariants: A test called allvariants_2_0002 should exist")
dune_assert(TEST_EXISTS allvariants_2_0003 MESSAGE "allvariants: A test called allvariants_2_0003 should exist")