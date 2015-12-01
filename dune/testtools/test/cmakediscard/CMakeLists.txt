set(MYPARAM 0)
set(MYOTHERPARAM 1)

add_dune_system_test(SOURCE test.cc
                     INIFILE discard.mini
                     BASENAME dt1
                     CREATED_TARGETS ct1
                    )
message("DT1: ${ct1}")
dune_assert(LIST_LENGTH ct1 1 MESSAGE "Error in discard test 1")

set(MYOTHERPARAM 0)

add_dune_system_test(SOURCE test.cc
                     INIFILE discard2.mini
                     BASENAME dt2
                     CREATED_TARGETS ct2
                    )
message("DT2: ${ct2}")
dune_assert(LIST_LENGTH ct2 0 MESSAGE "Error in discard test 2")
