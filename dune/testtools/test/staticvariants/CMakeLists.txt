add_static_variants(SOURCE source.cc INIFILE statictest.mini DEBUG BASENAME statictest TARGETS targetlist)
message("Targets generated for staticvariants testsuite: ${targetlist}")
