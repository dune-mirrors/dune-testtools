from __future__ import absolute_import

from .command import meta_ini_command, CommandType

@meta_ini_command(name="exclude", returnConfigs=True)
def _exclude(configs=None, key=None):
    return [c for c in configs if not eval(c[key])]

@meta_ini_command(name="label", argc=2, argdefaults=[None, "PRIORITY"], returnValue=False)
def _label(config=None, value=None, args=None):
    if eval(value):
        config["__STATIC.LABELS." + args[1]] = args[0]
