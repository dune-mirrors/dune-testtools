add_subdirectory(dune)
add_subdirectory(scripts)
add_subdirectory(wrapper)

dune_symlink_to_source_files(NAMES
  MANIFEST.in  pytest.ini  README  tests
)

dune_python_install_package(PATH .)
