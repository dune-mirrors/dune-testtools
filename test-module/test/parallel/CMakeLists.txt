dune_add_system_test(SOURCE source.cc
                     BASENAME parallel
                     INIFILE test.mini
                     CREATED_TARGETS output
                     SCRIPT dune_execute_parallel.py
                     ${DEBUG_MACRO_TESTS})

add_dune_mpi_flags(${output})

dune_assert(COND TARGET parallel_1 MESSAGE "parallel: A target named parallel_1 should have been generated")
dune_assert(COND TARGET parallel_2 MESSAGE "parallel: A target named parallel_2 should have been generated")
dune_assert(LIST_LENGTH output 2 MESSAGE "parallel: Two executables should have been generated")
dune_assert(TEST_EXISTS parallel_1_0000 MESSAGE "parallel: A test called parallel_1_0000 should exist")
dune_assert(TEST_EXISTS parallel_1_0001 MESSAGE "parallel: A test called parallel_1_0001 should exist")
dune_assert(TEST_EXISTS parallel_2_0002 MESSAGE "parallel: A test called parallel_2_0001 should exist")
dune_assert(TEST_EXISTS parallel_2_0003 MESSAGE "parallel: A test called parallel_2_0002 should exist")
