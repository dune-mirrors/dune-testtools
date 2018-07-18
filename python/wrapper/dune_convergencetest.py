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

If you use the functionality of the ``Dune::OutputTree`` class and its
method ``setConvergenceData(const T1& norm, const T2& quantity)`` the
convergence rate is automatically calculated from the norm and the given
scale quantity (e.g. h_max, delta_t). There is no further need to specify
how and where the output data is stored.

It is also possible to conduct more than one convergence test during the
same program run. This is of particular interest if you want to
* check convergence in more than one norm (L2, H1...)
* check convergence for systems of PDEs (rates might differ per component).
In order to achieve this you can substructure the configuration section
and list all subsections in the ``testsections`` key. The following example
treats a Q1/Q2 Taylor Hood Element.

.. code-block:: ini

    [wrapper.convergencetest]
    testsections = pressure velocity

    [wrapper.convergencetest.pressure]
    expectedrate = 1.0

    [wrapper.convergencetest.velocity
    expectedrate = 2.0


Omitting the testsections key will result in the configuration values being read
directly from the ``wrapper.convergencetest`` section.
"""
if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.convergencetest import call

    args = get_args()
    sys.exit(call(args["exec"], args["ini"]))
