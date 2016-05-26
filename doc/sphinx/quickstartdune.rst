Quick start guide (dune module)
*******************************

This document will show you the first steps to use system testing in your dune module.
Under a system test with ``dune-testtools`` we understand

* a single source file making use of several dune features,
* a so called meta ini configuration file,
* a test wrapper to determine success or failure.

They together describe a collection of tests. The collection of test gets generated
by static or dynamic variations of the source code. The variations are defined through
the meta ini configuration file.

Module setup
============

Suppose you have an existing dune module ``dune-foo`` and you want to write your first
system test. You probably already have dune-testtools, if not clone ``dune-testtools``
and its dependency ``dune-python`` from the Dune GitLab server.

.. code-block:: shell

    git clone https://gitlab.dune-project.org/quality/dune-python.git
    git clone https://gitlab.dune-project.org/quality/dune-testtools.git

``dune-foo`` needs to know about ``dune-testtools`` in order to use its
functionality, so we have to add it to the dependencies in the ``dune.module``
file of the project. Having it in the ``Depends:`` list is necessary to
emable the functions of the ``dune-testtools`` CMake modules.

.. code-block:: ini
    :caption: ``dune.module`` file of project ``dune-foo``

    Module: dune-foo
    Version: 3.0git
    Maintainer: you@dune.org
    Depends: dune-common dune-testtools

.. note::
    You might have to delete the build directory
    of ``dune-foo`` and rebuild using dunecontrol
    to find dune-testtools.

Setting up a first system test
==============================

Assuming you have a ``test`` directory in your dune module, your source directory
for the system test should look something like this

.. code-block:: ini

    test
    |____ mysystemtest
    |     |___ source.cc
    :     |___ config.mini
          |___ CMakeLists.txt

First, let's have a look at ``CMakeLists.txt``. To add system tests ``dune-testtools``
provides a simple CMake macro. In the above setting, ``CMakeLists.txt`` could look like this

.. code-block:: cmake
    :caption: The ``CMakeLists.txt``

    dune_add_system_test(SOURCE source.cc
                         INIFILE config.mini
                         BASENAME mysystemtest)

The ``SOURCE`` and ``INIFILE`` parameter should be self-explanatory.

.. note::
    The file extension of the meta ini file is arbitrary, ``*.mini`` is good practice
    in distinction to normal ini files.

.. note::
    We assume here that your module uses ``dune_enable_all_packages()``. If you don't use
    the convienience macro you can get all generated CMake targets by specifying
    ``CREATED_TARGETS targets`` as additional parameter to the macro. You can then
    link libraries to the targets manually.

The ``BASENAME`` parameter defines a basename to be used for executables
created by the CMake macro. In case of static variations,
more than one executable will be created.

.. note::
    CMake targets have to be unique within the entire project. Choose your
    basename so that it conflict with other targets in your project can be ruled out.

Secondly, let's look at the meta ini file. Meta ini files are the heart of the
``dune-testtools`` project. They configure the system test and have a simple
syntax very similar to regular ini files used in Dune. Let's say your code has
the grid manager as template parameter (has to be known at compile time) and
a simple run-time parameter ``level`` that determines how often the initial grid
will be refined. To test the flexibility of your code you want to run it with
two grid managers and for three different refinement levels. Then, your
meta ini file could look like this

.. code-block:: ini
    :caption: The ``config.mini``

    level = 1, 2, 3 | expand

    [__static]
    GRID = Dune::YaspGrid<2>, Dune::UGGrid<2> | expand

This example will create two exectuables and in total 6 tests. As you can see
parameter variation are specified by using a comma-separated list as value for
the key-value pair. The ``expand`` command after the pipe tells ``dune-testtools``
to generate ini files for each comma-separated value. Multiple ``expand`` commands
lead to the combination of the parameter variations.

.. note::
    You have to have UGGrid installed to run this example.

.. note::
    You always have to find sensibel parameters for your test manually. However
    even then, the combinatorial expansion quickly generates a large number of tests.

Static parameters like the grid type need to be communicated to the build system
to generate different executables. To tell ``dune-testtools`` that a parameter
is static we list it under the ``[__static]`` group.

.. note::
    If your template type contains commas, they need to be escaped. Alternatively,
    you can put the whole type in quotation marks (``"Dune::FieldVector<2, 3>"``).

The static variable ``GRID`` that you defined under the ``[__static]`` section, will
be available as preprocessor variable in your source code. So the source code could
look like this

.. code-block:: cpp

    #include "config.h"

    #include <sstream>
    #include <string>
    #include <dune/common/parallel/mpihelper.hh>
    #include <dune/common/exceptions.hh>
    #include <dune/common/parametertree.hh>
    #include <dune/common/parametertreeparser.hh>
    #include <dune/grid/utility/structuredgridfactory.hh>
    #include <dune/grid/io/file/vtk.hh>
    #include <dune/grid/yaspgrid.hh>
    #include <dune/grid/uggrid.hh>

    int main(int argc, char** argv) try
    {
      // maybe initialize mpi
      Dune::MPIHelper::instance(argc, argv);

      // check if a single argument was supplied
      if (argc != 2)
        DUNE_THROW(Dune::InvalidStateException, "Please supply an ini file. Usage: ./" << argv[0] << " <inifile>");

      // load the parameter file
      Dune::ParameterTree params;
      Dune::ParameterTreeParser::readINITree(argv[1], params);

      // the grid type
      typedef GRIDTYPE Grid;

      // build a simple structured 2x2 unit square grid
      Dune::StructuredGridFactory<Grid> factory;
      auto grid = factory.createCubeGrid({0, 0}, {1, 1}, {{2, 2}});

      // refine the grid
      auto level = params.get<int>("level", 0);
      grid->globalRefine(level);

      // output the grid to vtk
      // note: a unique vtk filename can easily be generated in the meta ini file
      Dune::VTKWriter<typename Grid::LeafGridView> vtkwriter(grid->leafGridView());
      std::stringstream outputName;
      outputName << argv[0] << "_" << params.get<std::string>("level");
      vtkwriter.write(outputName.str());

      return 0;
    }
    // Error handler /////////////////
    catch (Dune::Exception e) {
        std::cerr << e << std::endl;
        return 1;
    }

Building and running the first system test
==========================================

Congratulations, you already set up your first system test.
We assume you already know how to configure and build Dune.
Using ``dunecontrol`` is the easiest.

.. code-block:: shell

    ./dune-common/bin/dunecontrol all

To configure the system test in case you already have a build-directory
from a dunecontrol run or otherwise, rerun CMake

.. code-block:: shell

    cmake build-cmake

.. note::
    This assumes you are using ``dunecontrol``'s default
    build directory structure with a ``build-cmake`` build
    directory in each module.

Now, like for other Dune tests you can build and run your tests with

.. code-block:: shell

    cd <builddir>
    make -j2 build_tests
    ctest -j2

.. note::
    The flag ``-j2`` builds and runs ctest in parallel on ``2`` cores. This doesn't
    mean that each individual test is run in parallel. For parallel testing have a look
    at the test wrapper :mod:`wrapper.execute_parallel` or the following
    :ref:`section <section_testwrappers>`.

Running the commands should produce the following or similar output

.. code-block:: shell

        Start 1: mysystemtest_0000_0000
        Start 2: mysystemtest_0000_0001
        Start 3: mysystemtest_0000_0002
        Start 4: mysystemtest_0001_0003
        Start 5: mysystemtest_0001_0004
        Start 6: mysystemtest_0001_0005
    1/6 Test #6: mysystemtest_0001_0005 ...........   Passed    0.40 sec
    2/6 Test #1: mysystemtest_0000_0000 ...........   Passed    0.43 sec
    3/6 Test #3: mysystemtest_0000_0002 ...........   Passed    0.43 sec
    4/6 Test #4: mysystemtest_0001_0003 ...........   Passed    0.43 sec
    5/6 Test #2: mysystemtest_0000_0001 ...........   Passed    0.43 sec
    6/6 Test #5: mysystemtest_0001_0004 ...........   Passed    0.42 sec

    100% tests passed, 0 tests failed out of 6

    Label Time Summary:
    DUNE_SYSTEMTEST    =   2.54 sec

    Total Test time (real) =   0.43 sec

.. _section_testwrappers:

Test wrappers
=============

Many times we don't only want to check exit codes of our tests to decide whether they
passed or failed. That's why with ``dune-testtools`` you can easily wrap your executable
and perform more elaborate result checking or execution. ``dune-testtools`` already provides
a number of useful :ref:`wrappers <thewrappers>`. With a little knowledge of Python it is also
easy to write your own wrapper. We want to demonstrate the
use of wrappers here briefly.

Suppose you want to run the tests we just wrote in parallel using ``8`` cores. The CMake macro
provides an optional argument for specifying a wrapper script. The modified ``CMakeLists.txt``
would look like this

.. code-block:: cmake
    :caption: The modified ``CMakeLists.txt``

    dune_add_system_test(SOURCE source.cc
                         INIFILE config.mini
                         BASENAME mysystemtest
                         SCRIPT dune_execute_parallel.py)

Conveniently, you can configure the wrapper script with your meta ini file.
To specifiy the number of processors we would modify ``config.mini`` like this

.. code-block:: ini
    :caption: The modified ``config.mini``

    level = 1, 2, 3 | expand

    [wrapper.execute_parallel]
    numprocessors = 8

    [__static]
    GRID = Dune::YaspGrid<2>, Dune::UGGrid<2> | expand

Finally, you can build and run your tests in parallel!

.. note::
    You might have noticed the following: Also the number of processors is a meta ini
    variable that can be expanded. This offers you to run different configurations
    on a different number of processors!
