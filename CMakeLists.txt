cmake_minimum_required(VERSION 3.16)
project(dune-testtools CXX)

if(NOT (dune-common_DIR OR dune-common_ROOT OR
      "${CMAKE_PREFIX_PATH}" MATCHES ".*dune-common.*"))
    string(REPLACE  ${CMAKE_PROJECT_NAME} dune-common dune-common_DIR
      ${PROJECT_BINARY_DIR})
endif()

#find dune-common and set the module path
find_package(dune-common REQUIRED)
list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake/modules"
  ${dune-common_MODULE_PATH})

#include the dune macros
include(DuneMacros)

if(dune-common_VERSION VERSION_GREATER_EQUAL 2.11)
  dune_policy(SET DP_DEFAULT_INCLUDE_DIRS NEW)
endif()

# start a dune project with information from dune.module
dune_project()

dune_add_library(dunetesttools INTERFACE
  EXPORT_NAME Testtools
  LINK_LIBRARIES Dune::Common)

if(dune-common_VERSION VERSION_GREATER_EQUAL 2.11)
  dune_default_include_directories(dunetesttools INTERFACE)
endif()

set(DUNE_TESTTOOLS_PATH ${PROJECT_SOURCE_DIR})

dune_python_configure_package(PATH python)

dune_python_add_test(NAME pytest
                     MODULE pytest
                     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/python
                     )

dune_python_add_test(NAME pep8
                     MODULE pytest --flake8
                     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/python
                     )

add_subdirectory(dune)
add_subdirectory(doc)
add_subdirectory(cmake)

# Use a custom section to export testtool module path for downstream modules.
set(DUNE_CUSTOM_PKG_CONFIG_SECTION "
set(DUNE_TESTTOOLS_PATH \"${PROJECT_SOURCE_DIR}\")
")

# finalize the dune project, e.g. generating config.h etc.
finalize_dune_project()
