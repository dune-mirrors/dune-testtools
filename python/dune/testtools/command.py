""" Collection of all the commands that can be applied in a meta ini file

.. currentmodule:: dune.testtools.command

Some easy commands are defined and implemeted here. All others get imported from here.
This is necessary to have a reliably full command registry.

Commands
++++++++

.. _eval:
.. metaini_command:: eval

    The command `eval` evaluates basic math operations.
    The operands can be meta ini variables (inside bracket operators).

    Example:

    In the following code example `c` will be `4`.

    .. code-block:: ini

        a = 2
        b = 2
        c = {a} * {b} | eval

    `pi` will be replaced by the number pi.
    The evaluation supports unary and binary operators like

    - addition (`+`)
    - subtraction (`-`)
    - multiplication (`*`)
    - floating point division (`/`)
    - a power function(`^`)
    - unary minus (`-`).

.. _tolower:
.. metaini_command:: tolower

    The command `tolower` converts the value to lower case.
    It complements the command `toupper`.

    Example:

    In the following code example `a` will be `variable`.

    .. code-block:: ini

        a = VARIABLE | to_lower


.. _toupper:
.. metaini_command:: toupper

    The command `toupper` converts the value to upper case.
    It complements the command `tolower`.

    Example:

    In the following code example `a` will be `VARIABLE`.

    .. code-block:: ini

        a = variable | to_upper

"""
from __future__ import absolute_import

from dune.testtools.command_infrastructure import meta_ini_command, command_registry, CommandType, apply_commands, command_count

# import all those modules that do define commands.
# Only this way we can ensure that the registry is completely
# build up.
from dune.testtools.uniquenames import *
from dune.testtools.metaini import *
from dune.testtools.conditionals import *
from dune.testtools.wrapper.convergencetest import *
from dune.testtools.testdiscarding import *


@meta_ini_command(name="tolower")
def _cmd_to_lower(value=None):
    """Defines the meta ini command tolower"""
    return value.lower()


@meta_ini_command(name="toupper")
def _cmd_to_upper(value=None):
    """Defines the meta ini command toupper"""
    return value.upper()


@meta_ini_command(name="eval", ctype=CommandType.POST_FILTERING)
def _eval_command(value=None):
    """Defines the meta ini command eval"""

    import ast
    import math
    import operator as op

    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg}

    def eval_(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.Name):  # <constant>
            if node.id.lower() == "pi":
                return math.pi
            else:
                raise ValueError(node.id)
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](eval_(node.left), eval_(node.right))
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_(node.operand))
        else:
            raise TypeError(node)

    return str(eval_(ast.parse(value, mode='eval').body))
