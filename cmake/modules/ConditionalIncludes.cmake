# A module managing conditional includes for the CMake build system
#
# .. cmake_function:: resolve_conditional_includes
#
#    .. cmake_brief::
#
#        Implement a special mechanism for the resolution of conditional
#        includes.
#
#    .. cmake_param:: target
#       :required:
#       :single:
#       :positional:
#
#       The CMake target to operate on.
#
#    .. cmake_param:: definitions
#       :required:
#       :single:
#       :positional:
#
#       The list of preprocessor defines that includes depend on.
#
# .. note::
#
#    This currently not used productively. The alternative is to use
#    the ninja generator, which does dependency extraction differently.
#
#    CMake does not rely on the compiler to determine the dependencies of a
#    target. Unfortunately, it does not provide a full c preprocessor standard
#    implementation either. The issue is documented here:
#
#    http://public.kitware.com/Bug/print_bug_page.php?bug_id=11985
#
#    Preprocessor-macro-dependant include directives are pretty common in Dune.
#    Those are not picked up correctly.
#
#    In the context of system testing, this is not acceptable. Using static
#    switches to define the grid to be used will be a common pattern. A change to
#    one grid should only trigger rebuilds on those tests, that are actually using
#    that grid.
#
#    This module introduces a work-around based on the target property
#    :code:`IMPLICIT_DEPENDS_INCLUDE_TRANSFORM`, which allows giving preprocessor macros
#    to the CMake dependency parser. Those macros are applied to include lines only.
#
#    Usage:
#
#    The following code snippet, one would usually use
#
#    ::
#
#       #ifdef SOME_VAR
#       #include <some/header.hh>
#       #endif
#
#    translate to the following statement:
#
#    ::
#
#       #include SOME_VAR_CONDITIONAL_INCLUDE(some/header.hh)
#
#    The new syntax is only valid, if the macro :code:`resolve_conditional_includes` has been
#    called with the target (AFTER all compile definitions are added) and the list of
#    compile definitions, that should be resolved.
#

macro(resolve_conditional_includes target definitions)
  # get the compile definitions currently set on the target
  get_property(target_defs TARGET ${target} PROPERTY COMPILE_DEFINITIONS)

  # process one definition given to the macro after the other
  foreach(def ${definitions})
    # check whether that definition exists on the target
    list(FIND target_defs ${def} ${def}_FOUND)
    if(NOT ${${def}_FOUND} EQUAL -1)
      # the definition is found: Define the macro as identity for both CMake Parser and C preprocessor
      set_property(TARGET ${target} APPEND PROPERTY IMPLICIT_DEPENDS_INCLUDE_TRANSFORM "${def}_CONDITIONAL_INCLUDE(%)=<%>")
      # appending to the compile flags property is buggy in CMake: it produces semicolons in the output
      get_property(flags TARGET ${target} PROPERTY COMPILE_FLAGS)
      set(flags "${flags} -D\"${def}_CONDITIONAL_INCLUDE\(h\)=<h>\"")
      set_property(TARGET ${target} PROPERTY COMPILE_FLAGS ${flags})
    else()
      # the definition is not found: Ignore this line in the CMake Parser and include some trivial macro in C preprocessor
      set_property(TARGET ${target} APPEND PROPERTY IMPLICIT_DEPENDS_INCLUDE_TRANSFORM "${def}_CONDITIONAL_INCLUDE(%)=")
      # appending to the compile flags property is buggy in CMake: it produces semicolons in the output
      get_property(flags TARGET ${target} PROPERTY COMPILE_FLAGS)
      set(flags "${flags} -D\"${def}_CONDITIONAL_INCLUDE\(h\)=<cstddef>\"")
      set_property(TARGET ${target} PROPERTY COMPILE_FLAGS ${flags})
    endif()
  endforeach()
endmacro()
