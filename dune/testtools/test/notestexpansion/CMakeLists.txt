dune_expand_metaini(INIFILE example.mini
                    SOURCE source.cc
                    BASENAME expansion
                    CREATED_TARGETS output)

dune_expand_metaini(INIFILE example.mini
                    NO_STATIC)

dune_assert(COND TARGET expansion_yasp MESSAGE "expansion: A target named expansion_yasp should have been generated")
dune_assert(COND TARGET expansion_ug MESSAGE "expansion: A target named expansion_ug should have been generated")
dune_assert(LIST_LENGTH output 2 MESSAGE "expansion: Two executables should have been generated")
