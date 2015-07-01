from __future__ import absolute_import
from argumentparser import get_args
from .call_executable import call
from ..fuzzy_compare_vtk import compare_vtk
from ..parser import parse_ini_file
import sys

if __name__ == "__main__":
    # Parse the given arguments
    args = get_args()

    # Execute the actual test!
    ret = call(args["exec"], args["ini"])

    # do the vtk comparison if execution was succesful
    if ret is 0:
        # Parse the inifile to learn about where the vtk file and its reference solution are located.
        ini = parse_ini_file(args["ini"])
        try:
            solution = ini["vtk.name"]
            ext = ini.get("vtk.extension", "vtu")
            reference = ini["vtk.reference"]
            ret = compare_vtk(solution + "." + ext, args["source"] + "/" + reference + "." + ext)
        except KeyError:
            sys.stdout.write("The test wrapper vtkcompare assumes keys vtk.name and vtk.reference to be existent in the inifile")
            ret = 1

    sys.exit(ret)
