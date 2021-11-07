add_python_targets(testtools
  command       __init__      parser      testdiscarding  writeini
  cmakeoutput   conditionals  metaini     uniquenames     command_infrastructure
  escapes       static_metaini 
)

add_subdirectory(parametertree)
add_subdirectory(wrapper)
