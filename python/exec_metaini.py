#!/usr/bin/python

from metaIni import expand_meta_ini
import sys

if (len(sys.argv) is 2):
    expand_meta_ini(sys.argv[1])
else:
    print "exec_metaIni expects exactly one command line parameter: the meta ini file"
