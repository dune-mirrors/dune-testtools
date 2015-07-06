from __future__ import absolute_import

from .command import meta_ini_command, CommandType

@meta_ini_command(name="exclude", returnConfigs=True)
def _exclude(configs=None, key=None):
    return [c for c in configs if not eval(c[key])]