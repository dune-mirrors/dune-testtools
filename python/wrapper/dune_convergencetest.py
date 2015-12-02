#!/usr/bin/env python

# A wrapper script that controls the execution of a convergence test

import sys

from dune.testtools.wrapper.argumentparser import get_args
from dune.testtools.wrapper.convergencetest import call

args = get_args()
sys.exit(call(args["exec"], args["ini"]))
