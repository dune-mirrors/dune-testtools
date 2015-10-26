if(dune-grid_FOUND)
  dune_add_test(SOURCES constructiontest.cc
                MPI_RANKS 2)
  dune_symlink_to_source_files(FILES ini test.msh)
endif()
