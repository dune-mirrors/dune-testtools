add_directory_test_target(_test_target)
add_dependencies(${_test_target} ${TESTPROGS})

add_executable(constructiontest constructiontest.cc)
dune_symlink_to_source_files(tree1.ini)
add_dune_ug_flags(constructiontest)
target_link_libraries(constructiontest ${DUNE_LIBS})
add_test(constructiontest constructiontest)