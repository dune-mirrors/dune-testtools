#!/usr/bin/env python

"""
This wrapper script does simply call the executable and forwards the return code.
This is used as the default wrapper script in the dune-testtools project.
"""
if __name__ == "__main__":

    import sys

    from dune.testtools.wrapper.argumentparser import get_args
    from dune.testtools.wrapper.call_executable import call

    # Parse the given arguments
    args = get_args()
    sys.exit(call(args["exec"], args["ini"]))
