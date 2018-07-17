set(MYPARAM 0)
set(MYOTHERPARAM 1)

dune_add_system_test(SOURCE test.cc
                     INIFILE discard.mini
                     BASENAME discardtest1
                     CREATED_TARGETS ct1
                    )

# How do we assert the new behaviour of adding 77 tests upon skipping?
#dune_assert(LIST_LENGTH ct1 1 MESSAGE "Error in discard test 1")

set(MYOTHERPARAM 0)

dune_add_system_test(SOURCE test.cc
                     INIFILE discard2.mini
                     BASENAME discardtest2
                     CREATED_TARGETS ct2
                    )

# How do we assert the new behaviour of adding 77 tests upon skipping?
# dune_assert(LIST_LENGTH ct2 0 MESSAGE "Error in discard test 2")
