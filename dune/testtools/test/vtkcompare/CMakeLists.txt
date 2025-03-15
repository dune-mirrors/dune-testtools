dune_symlink_to_source_files(FILES test.vtk test2.vtk)

dune_add_system_test(SOURCE source.cc
                     BASENAME vtkcompare_single
                     INIFILE test_single.mini
                     CREATED_TARGETS output
                     SCRIPT dune_vtkcompare.py
                     ${DEBUG_MACRO_TESTS})

dune_assert(COND TARGET vtkcompare_single MESSAGE "vtkcompare_single: A target named vtkcompare_single should have been generated")
dune_assert(LIST_LENGTH output 1 MESSAGE "vtkcompare_single: One executables should have been generated")
dune_assert(TEST_EXISTS vtkcompare_single_ MESSAGE "vtkcompare_single: A test called vtkcompare_single_ should exist")

dune_add_system_test(SOURCE source.cc
                     BASENAME vtkcompare_multiple
                     INIFILE test_multiple.mini
                     CREATED_TARGETS output
                     SCRIPT dune_vtkcompare.py
                     ${DEBUG_MACRO_TESTS})

dune_assert(COND TARGET vtkcompare_multiple MESSAGE "vtkcompare_multiple: A target named vtkcompare_multiple should have been generated")
dune_assert(LIST_LENGTH output 1 MESSAGE "vtkcompare_multiple: One executables should have been generated")
dune_assert(TEST_EXISTS vtkcompare_multiple_ MESSAGE "vtkcompare_multiple: A test called vtkcompare_multiple_ should exist")

dune_add_system_test(SOURCE source_parallel.cc
                     BASENAME vtkcompare_parallel
                     INIFILE test_parallel.mini
                     CREATED_TARGETS parallel_output
                     SCRIPT dune_vtkcompare.py
                     ${DEBUG_MACRO_TESTS})

add_dune_mpi_flags(${parallel_output})

dune_assert(COND TARGET vtkcompare_parallel_1 MESSAGE "vtkcompare_parallel: A target named vtkcompare_parallel_1 should have been generated")
dune_assert(COND TARGET vtkcompare_parallel_2 MESSAGE "vtkcompare_parallel: A target named vtkcompare_parallel_2 should have been generated")
dune_assert(LIST_LENGTH parallel_output 2 MESSAGE "vtkcompare_parallel: Two executables should have been generated")
dune_assert(TEST_EXISTS vtkcompare_parallel_1_0000 MESSAGE "vtkcompare_parallel: A test called vtkcompare_parallel_1_0000 should exist")
dune_assert(TEST_EXISTS vtkcompare_parallel_1_0001 MESSAGE "vtkcompare_parallel: A test called vtkcompare_parallel_1_0001 should exist")
dune_assert(TEST_EXISTS vtkcompare_parallel_2_0002 MESSAGE "vtkcompare_parallel: A test called vtkcompare_parallel_2_0001 should exist")
dune_assert(TEST_EXISTS vtkcompare_parallel_2_0003 MESSAGE "vtkcompare_parallel: A test called vtkcompare_parallel_2_0002 should exist")

