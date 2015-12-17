dune_cmake_sphinx_doc(SPHINX_CONF ${CMAKE_CURRENT_SOURCE_DIR}/conf.py.in
                      RST_SOURCES index.rst
                                  cmake.rst
                                  metaini.rst
                                  python.rst
                                  what.rst
                                  quickstartdune.rst
                                  testingtesttools.rst
                      MODULE_ONLY)

dune_symlink_to_source_files(FILES "_templates" "sphinx_metainicommand.py")
