#!/usr/bin/env python

"""
A wrapper script that controls the execution of a convergence test.

To be used in the CMake system test macro as follows

.. code-block:: cmake

    dune_add_system_test(...
                         SCRIPT dune_convergencetest.py
                         ...)

The wrapper can handle convergence tests where an exact solution is known.
The test has to have a parameter controlling the scale of the convergence
problem, i.e. timestep size, or grid refinement. The test also has to calculate
the difference to the exact solution is some norm. You can specify the
the parameter of interest in the meta ini file as in the following example

.. code-block:: ini

    [grid]
    level = 1, 2, 3, 4 | convergencetest

The convergence test can then be further configured through
the meta ini file as follows

.. code-block:: ini

    [wrapper.convergencetest]
    expectedrate = 2.0
    absolutedifference = 0.1

This will calculate the convergence rate and will mark the test as
failed if it's more than ``0.1`` different from ``2.0``.

If you use the ini functionality of ``Dune::OutputTree`` class and its
method ``setConvergenceData(const T1& norm, const T2& quantity)`` the
convergence rate is automatically calculated from the norm and the given
scale quantity (e.g. h_max, delta_t). If you output the quantities manually
you have to specify the keys that the wrapper has to search for when calculating
the rate as follows

.. code-block:: ini

    [wrapper.convergencetest]
    expectedrate = 2.0
    normkey = l2_norm
    scalekey = h_max

You the have to make sure to output your data in ini file format like this
for every run

.. code-block:: ini

    l2_norm = 1e-5
    h_max = 1e-3

"""
if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.convergencetest import call

    args = get_args()
    sys.exit(call(args["exec"], args["ini"]))
