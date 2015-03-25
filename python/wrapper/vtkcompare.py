from argumentparser import get_args
from call_executable import call
from fuzzy_compare_vtk import compare_vtk
from parseIni import parse_ini_file
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
        sys.stderr.write(ini["vtk.name"] + ".vtu")
        sys.stderr.write(args["source"] + ini["vtk.reference"] + ".vtu")
        ret = compare_vtk(ini["vtk.name"] + ".vtu", args["source"] + "/" + ini["vtk.reference"] + ".vtu")

    sys.exit(ret)
