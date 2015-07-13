from __future__ import absolute_import
from ..parser import *
from ..metaini import *
from ..command import meta_ini_command, CommandType
from ..command_infrastructure import *
from ..writeini import write_dict_to_ini
import os
import sys
import math
import subprocess

class ConvergenceTestFactory:
    index = 0

@meta_ini_command(name="convergencetest", argc=1, ctype=CommandType.POST_EXPANSION)
def _get_convergence_test(config=None, key=None, value=None, args=None, configs=None):
    """This command outputs a set of meta ini files each configuring a convergence test"""
    if not args[0]:
        # No argument given defaults to test key. This is converted to expand making the result and expandable meta ini file
        config[key] = value + "| expand"
        config["__convergencetest.testid"] = ConvergenceTestFactory.index
        ConvergenceTestFactory.index = ConvergenceTestFactory.index + 1
        # specify all default keys if not specified already
        if "__convergencetest.absolutedifference" not in config:
            config["__convergencetest.absolutedifference"] = 0.1
        if "__convergencetest.normkey" not in config:
            config["__convergencetest.normkey"] = 'norm'
        if "__convergencetest.scalekey" not in config:
            config["__convergencetest.scalekey"] = 'hmax'
        if "__convergencetest.output_extension" not in config:
            config["__convergencetest.output_extension"] = 'out'

    # write as key value pairs in a private section
    if args[0] == "rate":
        config["__convergencetest.expectedrate"] = value
    elif args[0] == "diff":
        config["__convergencetest.absolutedifference"] = value
    elif args[0] == "norm_outputkey":
        config["__convergencetest.normkey"] = value
    elif args[0] == "scale_outputkey":
        config["__convergencetest.scalekey"] = value
    elif args[0] == "output_extension":
        config["__convergencetest.output_extension"] = value

    # expand the key
    apply_commands(configs, CommandToApply("expand", None, key))


def call(executable, metaini=None):
    # check for the meta ini file
    if not metaini:
        sys.stderr.write("No meta ini file found for this convergence test!")
        return 1

    # expand the meta ini file
    configurations = expand_meta_ini(metaini)

    # execute all runs with temporary ini files and process the temporary output
    output = []
    for c in configurations:
        # write a temporary ini file
        write_dict_to_ini(c, "temp.ini")

        # execute the run
        command = ['./' + executable]
        iniinfo = parse_ini_file(metaini)
        if "__inifile_optionkey" in iniinfo:
            command.append(iniinfo["__inifile_optionkey"])
        command.append('temp.ini')

        if subprocess.call(command):
            return 1

        # collect the information from the output file
        try:
            output.append(parse_ini_file(os.path.basename(c["__name"]) + "." + c["__convergencetest.output_extension"])[0])
        except Exception as e:
            raise e
            return 1

        # remove temporary files
        os.remove(os.path.basename(c["__name"]) + "." + c["__convergencetest.output_extension"])
        os.remove("temp.ini")

    # calculate the rate according to the outputted data
    for idx, c in list(enumerate(configurations))[:-1]:
        norm1 = float(output[idx]["__convergencetest.normkey"])
        norm2 = float(output[idx+1]["__convergencetest.normkey"])
        hmax1 = float(output[idx]["__convergencetest.scalekey"])
        hmax2 = float(output[idx+1]["__convergencetest.scalekey"])
        rate = math.log(norm2/norm1)/log(hmax2/hmax1)
        # compare the rate to the expected rate
        if math.fabs(rate-output[idx]["__convergencetest.expectedrate"]) > output[idx]["__convergencetest.absolutedifference"]:
            sys.stderr.write("Test failed because the absolute difference between the \
                             calculated convergence rate ({}) and the expected convergence rate ({}) was too \
                             large.\n".format(rate, output[idx]["__convergencetest.expectedrate"]))
            return 1

    # if we got here everything passed
    return 0

# The script called by cmake
if __name__ == "__main__":
    # Parse the given arguments
    from .argumentparser import get_args
    args = get_args()
    sys.exit(call(args["exec"], args["ini"]))
