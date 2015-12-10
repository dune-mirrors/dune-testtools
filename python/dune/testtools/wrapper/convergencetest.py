from __future__ import absolute_import
from dune.testtools.parser import *
from dune.testtools.metaini import *
from dune.testtools.command import meta_ini_command, CommandType
from dune.testtools.command_infrastructure import *
from dune.testtools.writeini import write_dict_to_ini
import os
import sys
import math
import subprocess


@meta_ini_command(name="convergencetest", argc=0, ctype=CommandType.PRE_EXPANSION)
def _get_convergence_test(key=None, value=None, config=None, args=None, commands=None):
    """This command overwrites convergencetest key to fool resolution"""

    config["__local.wrapper.convergencetest.value"] = value
    # move possible commands to the new key
    replace_command_key(commands, key, newkey="__local.wrapper.convergencetest.value")
    # add the command that will retrieve the original convergence test value after expansion and resolution
    commands[CommandType.POST_RESOLUTION].append(CommandToApply(name="convergencetest_retrieve", args=[], key=key))
    # escape the resolution brackets as we don't want them to be resolved now
    return "\\{" + key + "\\}"


@meta_ini_command(name="convergencetest_retrieve", ctype=CommandType.POST_RESOLUTION)
def _get_convergence_test(key=None, value=None, config=None):
    """This command replaces the convergence test key by the original unexpanded value
       leaving a metaini file configuring a convergence test"""
    return config["__local.wrapper.convergencetest.value"] + " | expand"


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
        # check if all necessary keys are given
        if "wrapper.convergencetest.expectedrate" not in c:
            sys.stderr.write("The convergencetest wrapper excepts a key wrapper.convergencetest.expectedrate \
                              to be present in the ini file!")
            return 1

        # specify all default keys if not specified already
        if "wrapper.convergencetest.absolutedifference" not in c:
            c["wrapper.convergencetest.absolutedifference"] = '0.1'
        if "wrapper.convergencetest.normkey" not in c:
            c["wrapper.convergencetest.normkey"] = 'norm'
        if "wrapper.convergencetest.scalekey" not in c:
            c["wrapper.convergencetest.scalekey"] = 'hmax'
        if "__output_extension" not in c:
            c["__output_extension"] = 'out'

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
        norm1 = float(output[idx][c["wrapper.convergencetest.normkey"]])
        norm2 = float(output[idx + 1][c["wrapper.convergencetest.normkey"]])
        hmax1 = float(output[idx][c["wrapper.convergencetest.scalekey"]])
        hmax2 = float(output[idx + 1][c["wrapper.convergencetest.scalekey"]])
        rate = math.log(norm2 / norm1) / math.log(hmax2 / hmax1)
        # compare the rate to the expected rate
        if math.fabs(rate - float(c["wrapper.convergencetest.expectedrate"])) > float(c["wrapper.convergencetest.absolutedifference"]):
            sys.stderr.write("Test failed because the absolute difference between the \
                             calculated convergence rate ({}) and the expected convergence rate ({}) was too \
                             large.\n".format(rate, c["wrapper.convergencetest.expectedrate"]))
            return 1

    # if we got here everything passed
    return 0
