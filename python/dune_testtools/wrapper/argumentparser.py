""" A module that defines an Argument parser for test wrapper scripts

The argument parser defines the interface between the cmake macros of
dune-testtools and python test wrappers. All parameters listed here
will be set by cmake correctly.
"""
from __future__ import absolute_import
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--exec', help='The executable', required=True)
    parser.add_argument('-i', '--ini', help='The inifile', required=True)
    parser.add_argument('-s', '--source', help='The source directory')
    return vars(parser.parse_args())
