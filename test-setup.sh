#!/usr/bin/env bash

rm -rf build-testmod
mkdir build-testmod
cd build-testmod

cmake \
  -Ddune-common_DIR=${dune-common_DIR} \
  -Ddune-geometry_DIR=${dune-geometry_DIR} \
  -Ddune-grid_DIR=${dune-grid_DIR} \
  -Ddune-alugrid_DIR=${dune-alugrid_DIR} \
  -Ddune-testtools_DIR=${CMAKE_BINARY_DIR} \
  -DDUNE_PYTHON_VIRTUALENV_PATH=${DUNE_PYTHON_VIRTUALENV_PATH} \
  ${CMAKE_SOURCE_DIR}/test-module

make
make build_tests
ctest
