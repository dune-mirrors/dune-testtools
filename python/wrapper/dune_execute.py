#!/usr/bin/env python

"""
This wrapper script does simply call the executable and forwards the return code.
This is used as the default wrapper script in the dune-testtools project.

If you want to explitly specify the wrapper for clarity use

.. code-block:: cmake

    dune_add_system_test(...
                         SCRIPT dune_execute.py
                         ...)
"""
if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.call_executable import call

    # Parse the given arguments
    args = get_args()
    sys.exit(call(args["exec"], args["ini"]))
