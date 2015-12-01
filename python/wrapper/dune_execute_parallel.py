#!/usr/bin/env python

# This wrapper script does execute a given application in parallel

import sys

from dune.testtools.wrapper.argumentparser import get_args
from dune.testtools.wrapper.call_executable import call_parallel


# Parse the given arguments
args = get_args()
if not args["mpi_exec"]:
    sys.stderr.write("call_parallel.py: error: Mpi executable not given.\n" +
                     "usage: call_parallel.py [-h] -e EXEC -i INI --mpi-exec MPI_EXEC \n" +
                     "                        --mpi-numprocflag MPI_NUMPROCFLAG [-s SOURCE]\n")
    sys.exit(1)
if not args["mpi_numprocflag"]:
    sys.stderr.write("call_parallel.py: error: Mpi number of processes flag not given.\n" +
                     "usage: call_parallel.py [-h] -e EXEC -i INI --mpi-exec MPI_EXEC \n" +
                     "                         --mpi-numprocflag MPI_NUMPROCFLAG [-s SOURCE]\n")
    sys.exit(1)

# check if flags are provided
if args["mpi_preflags"] == ['']:
    args["mpi_preflags"] = None
if args["mpi_postflags"] == ['']:
    args["mpi_postflags"] = None

sys.exit(call_parallel(args["exec"], args["mpi_exec"], args["mpi_numprocflag"], args["mpi_preflags"], args["mpi_postflags"], args['max_processors'][0], inifile=args["ini"]))
