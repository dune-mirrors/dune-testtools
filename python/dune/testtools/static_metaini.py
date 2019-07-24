from __future__ import absolute_import
from dune.testtools.parser import CommandToApply
from dune.testtools.metaini import expand_meta_ini
from dune.testtools.command import apply_commands
import sys
import argparse


def extract_static_info(metaini, section='__static', add_guards=False):
    static_section = expand_meta_ini(metaini, whiteFilter=(section, "__exec_suffix", "__cmake_guards"), addNameKey=False)

    # make the found exec suffixes unique
    if "__exec_suffix" not in static_section[0]:
        static_section[0]["__exec_suffix"] = ""
    cmd = [CommandToApply(name="unique", args=[], key="__exec_suffix")]
    apply_commands(static_section, cmd)

    # construct a dictionary from the static information. This can be passed to CMake
    static = {}
    # we need a list of extracted compile definitions names
    static["__STATIC_DATA"] = []
    # The special key __CONFIGS holds a list of configuration names
    static["__CONFIGS"] = []

    # extract the data from the configurations
    for conf in static_section:
        static["__CONFIGS"].append(conf["__exec_suffix"])

        # copy the entire data
        if section in conf:
            for key in conf[section]:
                if key not in static["__STATIC_DATA"]:
                    static["__STATIC_DATA"].append(key)

            static[conf["__exec_suffix"]] = conf[section]

        # Now update the list of CMake guards
        if add_guards:
            if "__cmake_guards" in conf:
                static.setdefault(conf["__exec_suffix"], {})
                static[conf["__exec_suffix"]]['__GUARDS'] = conf["__cmake_guards"].values()

    return static
