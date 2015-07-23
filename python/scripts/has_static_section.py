#!/usr/bin/env python

from dune_testtools.metaini import expand_meta_ini
import argparse
import sys

"""Check if there are static variations in a metaini file"""
# define the argument parser for this script
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ini', help='The inifile', required=True)
args = vars(parser.parse_args())
configurations = expand_meta_ini(args['ini'], whiteFilter=("__static",), addNameKey=False)
if len(configurations) > 1:
        sys.exit(1)
sys.exit(0)
