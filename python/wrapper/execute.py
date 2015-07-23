#!/usr/bin/env python

# This wrapper script does simply call the executable and forwards the return code.
# This is used as the default wrapper script in the dune-testtools project.

import sys

from dune_testtools.wrapper.argumentparser import get_args
from dune_testtools.wrapper.call_executable import call

# Parse the given arguments
args = get_args()
sys.exit(call(args["exec"], args["ini"]))
