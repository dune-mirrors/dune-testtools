"""A module implementing commands for conditionals

.. currentmodule:: dune.testtools.conditionals

It is possible in meta ini syntax to state values without keys
if they have a command applied that support conditionals. The value
is then evaluated as a Python Boolean expression (after resolution).

Commands
++++++++

.. _exclude:
.. metaini_command:: exclude
    :operates_on_value:

    Using the `exclude` command on a non-key value,
    evaluates the value as a bolean expression. If the bolean expression evaluates to `False`,
    the respective configuration (ini file) will be discarded and no test will be produced.

    Example:

    In the following code example no ini file
    in which `DIM` is `1` and `GRID` is `ug` will be produced.

    .. code-block:: ini

        {__static.GRID} == ug and {__static.DIM} == 1 | exclude

        [__static]
        DIM = 1, 2 | expand
        GRID = ug, yasp | expand


.. _label:
.. metaini_command:: label
    :operates_on_value:

    .. metaini_command_arg:: LABEL
        :required:
        :multi:

        A label to be used by the build system. Labels can
        be used to specify types of tests, e.g. `CONTINUOUS`, `NIGHTLY`, `WEEKLY`
        for the frequency of automated testing.

    Using the command `label <LABEL>` on a non-key value
    evaluates the value as a bolean expression. If the bolean expression evaluates to `True`
    the respective configuration (ini file) produces a test with the given labels attached.

    Example:

    In the following code example all configurations
    with `resolution` being greater than or equal `5` will get the label NIGHTLY attached. The
    label can be used e.g. by CTest to only run a test once a night.

    .. code-block:: ini

        resolution = 3, 5, 7, 9 | expand
        if {resolution} >= 5 | label NIGHTLY

"""

from __future__ import absolute_import
from dune.testtools.command import meta_ini_command, CommandType


class _DummyEnvironment(dict):
    def __getitem__(self, key):
        return key


def eval_boolean(s):
    """ evaluate the given string `s` as a boolean expression """
    try:
        return eval(s, _DummyEnvironment())
    except SyntaxError:
        return False


@meta_ini_command(name="exclude", returnConfigs=True)
def _exclude(configs=None, key=None):
    """Defines the meta ini command exclude"""
    return [c for c in configs if not eval_boolean(c[key])]


@meta_ini_command(name="label", argc=2, argdefaults=[None, "PRIORITY"], returnValue=False)
def _label(config=None, value=None, args=None):
    """Defines the meta ini command label"""
    if eval_boolean(value):
        config["__LABELS." + args[1]] = args[0]
