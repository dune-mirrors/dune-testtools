add_subdirectory(constructiontest)
add_subdirectory(cmakediscard)
add_subdirectory(cmakepython)
add_subdirectory(staticvariants)
add_subdirectory(dynamicvariants)
add_subdirectory(onemacrodynamicvariants)
add_subdirectory(allvariants)
add_subdirectory(parallel)
add_subdirectory(convergencetest)
add_subdirectory(outputcompare)
add_subdirectory(vtkcompare)
add_subdirectory(notestexpansion)

dune_add_test(SOURCES outputtreetest.cc)

include(ConditionalIncludes)
dune_add_test(SOURCES triggertest.cc
              COMPILE_DEFINITIONS SWITCH1)
resolve_conditional_includes(triggertest "SWITCH1;SWITCH2")
