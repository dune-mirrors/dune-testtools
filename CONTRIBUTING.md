We are open to patch submissions. Please provide patches against current master
that are generated with:

`git format-patch -k`

Before submitting a patch we kindly ask you to run and check
our testing suite:

`make build_tests`
`ctest -j2`
`make pytest`


Please note the following:

STYLE GUIDE
===========

CMake:
------

* Always use empty end-clauses like:
```
if(SOME_VARIABLE)
  ...
else()
  ...
endif()
```
* use lowercase for all commands
* use uppercase for variables
* always use 2 spaces for indentation
* for new features always provide unittests
* document your code in Sphinx restructered text

Python
------

* follow PEP8 (see https://www.python.org/dev/peps/pep-0008/)
* you can test your files for PEP8 compliance with e.g. pytest --pep8
* make your code work with Python 2 and Python 3
* separate scripts and modules, scripts belong in the scripts folder
* provide unit tests for new features
* prefer named arguments
* function names are lower_case underscore
* variable names are lowercase camelCase
* class names are CamelCase
* file names are lowercase
* document your code in Sphinx restructered text

Ini-files
---------

* Meta ini file should prefer the *.mini extension
* keep all keys lowercase (except for keys exported as
  as compile definitions or labels in the static section)
* use groups to make things readable
* space separate key, "=", and value
* you can test meta ini files with the `dune_analysis.py` script
  provided with testtools
