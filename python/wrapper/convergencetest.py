#!/usr/bin/env python

# A wrapper script that controls the execution of a convergence test

import sys

from dune_testtools.wrapper.argumentparser import get_args
from dune_testtools.wrapper.convergencetest import call

args = get_args()
sys.exit(call(args["exec"], args["ini"]))