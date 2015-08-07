from __future__ import absolute_import
from dune_testtools.parser import *
from dune_testtools.metaini import *
from dune_testtools.command import meta_ini_command, CommandType
from dune_testtools.command_infrastructure import *
from dune_testtools.writeini import write_dict_to_ini
import os
import sys
import math
import subprocess


@meta_ini_command(name="convergencetest", argc=1, ctype=CommandType.PRE_EXPANSION)
def _get_convergence_test(key=None, value=None, config=None, args=None, commands=None):
    """This command overwrites convergencetest key to fool resolution"""
    if not args[0]:
        # specify all default keys if not specified already
        if "__convergencetest.absolutedifference" not in config:
            config["__convergencetest.absolutedifference"] = '0.1'
        if "__convergencetest.normkey" not in config:
            config["__convergencetest.normkey"] = 'norm'
        if "__convergencetest.scalekey" not in config:
            config["__convergencetest.scalekey"] = 'hmax'
        if "__output_extension" not in config:
            config["__output_extension"] = 'out'

        config["__local.__convergencetest.value"] = value
        # move possible commands to the new key
        replace_command_key(commands, key, newkey="__local.__convergencetest.value")
        # add the command that will retrieve the original convergence test value after expansion and resolution
        commands[CommandType.POST_RESOLUTION].append(CommandToApply(name="convergencetest_retrieve", args=[], key=key))
        # escape the resolution brackets as we don't want them to be resolved now
        return "\\{" + key + "\\}"
    else:
        # write as key value pairs in a private section
        if args[0] == "rate":
            config["__convergencetest.expectedrate"] = value
            replace_command_key(commands, key, newkey="__convergencetest.expectedrate")
        elif args[0] == "diff":
            config["__convergencetest.absolutedifference"] = value
            replace_command_key(commands, key, newkey="__convergencetest.absolutedifference")
        elif args[0] == "norm_outputkey":
            config["__convergencetest.normkey"] = value
            replace_command_key(commands, key, newkey="__convergencetest.normkey")
        elif args[0] == "scale_outputkey":
            config["__convergencetest.scalekey"] = value
            replace_command_key(commands, key, newkey="__convergencetest.scalekey")
        elif args[0] == "output_extension":
            config["__output_extension"] = value
            replace_command_key(commands, key, newkey="__output_extension")
        # the key is going to be deleted later as nkv are parsed into the __local section so out in a place holder
        return "__placeholder"


@meta_ini_command(name="convergencetest_retrieve", ctype=CommandType.POST_RESOLUTION)
def _get_convergence_test(key=None, value=None, config=None):
    """This command replaces the convergence test key by the original unexpanded value
       leaving a metaini file configuring a convergence test"""
    return config["__local.__convergencetest.value"] + " | expand"


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
        # write a temporary ini file. Prefix them with the name key to be unique
        tmp_file = c["__name"] + "_tmp.ini"
        write_dict_to_ini(c, tmp_file)

        # execute the run
        command = ['./' + executable]
        iniinfo = parse_ini_file(metaini)
        if "__inifile_optionkey" in iniinfo:
            command.append(iniinfo["__inifile_optionkey"])
        command.append(tmp_file)

        if subprocess.call(command):
            return 1

        # collect the information from the output file
        output.append([parse_ini_file(os.path.basename(c["__name"]) + "." + c["__output_extension"])][0])

        # remove temporary files
        os.remove(os.path.basename(c["__name"]) + "." + c["__output_extension"])
        os.remove(tmp_file)

    # calculate the rate according to the outputted data
    for idx, c in list(enumerate(configurations))[:-1]:
        norm1 = float(output[idx][c["__convergencetest.normkey"]])
        norm2 = float(output[idx + 1][c["__convergencetest.normkey"]])
        hmax1 = float(output[idx][c["__convergencetest.scalekey"]])
        hmax2 = float(output[idx + 1][c["__convergencetest.scalekey"]])
        rate = math.log(norm2 / norm1) / math.log(hmax2 / hmax1)
        # compare the rate to the expected rate
        if math.fabs(rate - float(c["__convergencetest.expectedrate"])) > float(c["__convergencetest.absolutedifference"]):
            sys.stderr.write("Test failed because the absolute difference between the \
                             calculated convergence rate ({}) and the expected convergence rate ({}) was too \
                             large.\n".format(rate, c["__convergencetest.expectedrate"]))
            return 1

    # if we got here everything passed
    return 0
