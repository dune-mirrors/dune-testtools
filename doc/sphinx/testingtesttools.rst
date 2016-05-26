Testing ``dune-testtools``
**************************

Yes, ``dune-testtools`` also gets tested itself. A number of tests
are already performed on each configure by CMake. ``dune-testtools``
provides assertions in CMake that can test if a specific target exists
or if a CTest has been generated. The build system tests get executed
every time if you call e.g.

.. code-block:: shell

    ./dune-common/bin/dunecontrol all

in the dune base directory. Further, ``dune-testtools`` provides some unit tests
(some of the unit tests might be considered system tests,
as they test our system test infrastructure). You can build and execute all
user interface tests by calling

.. code-block:: shell

    make build_tests
    ctest

in the top build directory. All tests should pass. Some might be skipped,
e.g. if you don't have MPI.

.. note::
    This works with ``dune-testtools`` git-master. When using Dune 2.4
    releases, testing still works with the old scheme. You can build
    all tests that belong to a system test by calling ``make BASENAME``,
    where ``BASENAME`` is the name given in the system test macro.

The machinery behind meta ini files is written in Python. Our Python
modules provide unit tests, too. You can run the Python test suite with

.. code-block:: shell

    make pytest

in the top build directory. This runs the tests and checks all modules
for PEP8 compliance. All tests should pass. Consider writing us if
some don't on your system.

Finally, this documentation can be build with

.. code-block:: shell

    make doc

in the top level build directory. You need the documentation tool
Sphinx installed on your system. An html documentation can then be
found under ``./doc/sphinx/html/index.html``.
