"""
This module provides methods for defining convergence tests.
"""

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
       leaving a meta ini file configuring a convergence test"""
    return config["__local.wrapper.convergencetest.value"] + " | expand"


def call(executable, metaini=None):
    # check for the meta ini file
    if not metaini:
        sys.stderr.write("No meta ini file found for this convergence test!")
        return 1

    # expand the meta ini file
    configurations = expand_meta_ini(metaini)

    # Find out in which sections the test data is
    testsections = configurations[0].get("wrapper.convergencetest.testsections", "").split()
    if testsections:
        testsections = ["wrapper.convergencetest.{}".format(s) for s in testsections]
    else:
        testsections = ["wrapper.convergencetest"]

    # execute all runs with temporary ini files and process the temporary output
    output = []
    for c in configurations:
        c.setdefault("__output_extension", "out")

        # write a temporary ini file. Prefix them with the name key to be unique
        tmp_file = c["__name"] + "_tmp.ini"
        write_dict_to_ini(c, tmp_file)

        # execute the run
        command = [executable]
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

    # store return value (because we do not want to return as soon as one section fails)
    returnvalue = 0

    # calculate the rate according to the outputted data
    for section in testsections:
        for idx, c in list(enumerate(configurations))[:-1]:
            # check if all necessary keys are given
            if "expectedrate" not in c[section]:
                sys.stderr.write("The convergencetest wrapper excepts a key expectedrate \
                                  in section {} of the ini file!".format(section))
                return 1

            # specify all default keys if not specified already
            c[section].setdefault("absolutedifference", "0.1")
            c.setdefault("__output_extension", "out")

            norm1 = float(output[idx][section]["norm"])
            norm2 = float(output[idx + 1][section]["norm"])
            hmax1 = float(output[idx][section]["scale"])
            hmax2 = float(output[idx + 1][section]["scale"])
            rate = math.log(norm2 / norm1) / math.log(hmax2 / hmax1)
            # test passes
            if math.fabs(rate - float(c[section]["expectedrate"])) <= float(c[section]["absolutedifference"]):
                sys.stdout.write("Test {} passed because the absolute difference "
                                 "between the calculated convergence rate ({}) "
                                 "and the expected convergence rate ({}) was within "
                                 "tolerance ({}). \n"
                                 .format(section, rate, c[section]["expectedrate"],
                                         c[section]["absolutedifference"]))
            # test fails because rates are off
            elif math.fabs(rate - float(c[section]["expectedrate"])) > float(c[section]["absolutedifference"]):
                sys.stderr.write("Test {} failed because the absolute difference "
                                 "between the calculated convergence rate ({}) "
                                 "and the expected convergence rate ({}) was greater "
                                 "than tolerance ({}). \n"
                                 .format(section, rate, c[section]["expectedrate"],
                                         c[section]["absolutedifference"]))
                returnvalue = 1
            # test fails because rates are nan or inf
            elif math.isnan(rate) or math.isinf(rate):
                sys.stderr.write("Test {} failed because calculated rate is ({})."
                                 "Expected was ({}) with tolerance ({}). \n"
                                 .format(section, rate, c[section]["expectedrate"], c[section]["absolutedifference"]))
                returnvalue = 1
            # if we are here, something unexpcted happened
            else:
                sys.stderr.write("Test {} failed for unknown reason with calculated rate ({}), "
                                 "expected rate ({}) and tolerance ({}). \n"
                                 .format(section, rate, c[section]["expectedrate"], c[section]["absolutedifference"]))
                returnvalue = 1

    return returnvalue
