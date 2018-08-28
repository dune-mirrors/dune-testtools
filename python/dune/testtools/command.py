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
    - a power function(`**`)
    - unary minus (`-`).

.. _tolower:
.. metaini_command:: tolower

    The command `tolower` converts the value to lower case.
    It complements the command `toupper`.

    Example:

    In the following code example `a` will be `variable`.

    .. code-block:: ini

        a = VARIABLE | tolower


.. _toupper:
.. metaini_command:: toupper

    The command `toupper` converts the value to upper case.
    It complements the command `tolower`.

    Example:

    In the following code example `a` will be `VARIABLE`.

    .. code-block:: ini

        a = variable | toupper

.. _toint:
.. metaini_command:: toint

    The command `toint` casts a given floating point number
    to an integer.

    Example:

    .. code-block:: ini

        a = 1.234 | toint

.. _repeat:
.. metaini_command:: repeat

    The command `repeat` repeats the value the given number of times
    with one whitespace as the separator. Note, that the argument to
    this command may itself use the curly bracket syntax.

    Example:

    .. code-block:: ini

        d = 3
        domain = 1.0 | repeat {dim}

.. _range:
.. metaini_command:: range

    Get a list of integers as provided by the python built-in command
    range and append it to the existing value. Arguments are given in
    order (stop, start, increment), where the latter two can be omitted
    (defaulting to 0 and 1 resp.). Note that there is no automatic expansion
    of the result, but the result can be expanded. However, the argument
    cannot be taken from an expanded key as this would involve a chicken
    egg situation (we basically had to decide between the two features).

    Example:

    .. code-block:: ini

        val = i | range 7 | expand

    The example results in 7 configuration files with val = i0, .., i6

.. _zfill:
.. metaini_command:: zfill

    Pad a given integer number with leading zeroes for it to be of the
    length given by the commands argument. Inspired and implemented by
    python str.zfill. This command is useful for numbered output filenames.

    Example:

    .. code-block:: ini

        val = 3 | zfill 4

    The example will have the val key read "0003".
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


@meta_ini_command(name="toint", ctype=CommandType.AT_RESOLUTION)
def _toint(value=None):
    """Cast the given floating point number to an integer"""
    return str(int(float(value)))


@meta_ini_command(name="repeat", ctype=CommandType.AT_RESOLUTION, argc=1)
def _repeat(value=None, args=None):
    return " ".join([value] * int(args[0]))


@meta_ini_command(name="eval", ctype=CommandType.AT_RESOLUTION)
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


@meta_ini_command(name="range", ctype=CommandType.PRE_EXPANSION, argc=3, argdefaults=(None, 0, 1))
def _range_command(value=None, args=None):
    # We need to switch the order of arguments here as python's range has a strange way of
    # having the only non-defaultable value as second instead of first parameter...
    return ", ".join("{}{}".format(value, n) for n in range(int(args[1]), int(args[0]), int(args[2])))


@meta_ini_command(name="zfill", argc=1, ctype=CommandType.AT_RESOLUTION)
def _zfill_command(value=None, args=None):
    return str(value).zfill(int(args[0]))
