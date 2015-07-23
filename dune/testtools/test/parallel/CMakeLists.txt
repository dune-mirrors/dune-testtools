add_dune_system_test(SOURCE source.cc
	                 BASENAME parallel
	                 INIFILE test.mini
	                 CREATED_TARGETS output
	                 SCRIPT execute_parallel.py
	                 ${DEBUG_MACRO_TESTS})

dune_assert(COND TARGET parallel_1 MESSAGE "parallel: A target named parallel_1 should have been generated")
dune_assert(COND TARGET parallel_2 MESSAGE "parallel: A target named parallel_2 should have been generated")
dune_assert(LIST_LENGTH output 2 MESSAGE "parallel: Two executables should have been generated")
dune_assert(TEST_EXISTS parallel_1_0002 MESSAGE "parallel: A test called parallel_1_0002 should exist")
dune_assert(TEST_EXISTS parallel_1_0003 MESSAGE "parallel: A test called parallel_1_0003 should exist")
dune_assert(TEST_EXISTS parallel_2_0000 MESSAGE "parallel: A test called parallel_2_0000 should exist")
dune_assert(TEST_EXISTS parallel_2_0001 MESSAGE "parallel: A test called parallel_2_0001 should exist")