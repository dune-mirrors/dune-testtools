dune_symlink_to_source_files(FILES "test.out")

dune_add_system_test(SOURCE source.cc
                     BASENAME outputcompare
                     INIFILE test.mini
                     CREATED_TARGETS output
                     SCRIPT dune_outputtreecompare.py
                     ${DEBUG_MACRO_TESTS})

dune_assert(COND TARGET outputcompare MESSAGE "outputcompare: A target named outputcompare should have been generated")
dune_assert(LIST_LENGTH output 1 MESSAGE "outputcompare: One executable should have been generated")
dune_assert(TEST_EXISTS outputcompare_ MESSAGE "outputcompare: A test called outputcompare_ should exist")
