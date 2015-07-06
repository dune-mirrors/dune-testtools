""" Collection of all the commands that can be applied in a meta ini file

Some easy commands are defined and implemeted here. All others get imported from here.
This is necessary to have a reliably full command registry.
"""
from __future__ import absolute_import

from .command_infrastructure import meta_ini_command, command_registry, CommandType, apply_commands, command_count

# import all those modules that do define commands.
# Only this way we can ensure that the registry is completely
# build up.
from .uniquenames import *
from .metaini import *
from .conditionals import *

@meta_ini_command(name="tolower")
def _cmd_to_lower(value=None):
    return value.lower()

@meta_ini_command(name="toupper")
def _cmd_to_upper(value=None):
    return value.upper()

@meta_ini_command(name="eval", ctype=CommandType.POST_FILTERING)
def _eval_command(value=None):
    import ast
    import math
    import operator as op

    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg}

    def eval_(node):
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.Name): # <constant>
            if node.id.lower() =="pi":
                return math.pi
            else:
                raise ValueError(node.id)
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return operators[type(node.op)](eval_(node.left), eval_(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_(node.operand))
        else:
            raise TypeError(node)

    return str(eval_(ast.parse(value, mode='eval').body))

@meta_ini_command(name="output_name", ctype=CommandType.POST_RESOLUTION, returnValue=False)
def _get_convergence_test_key(config=None, key=None, value=None, pipecommands=""):
    config["__output_name"] = value
    if "unique" in pipecommands:
        config[key] = value + pipecommands
    else:
        config[key] = value + "| unique" + pipecommands

@meta_ini_command(name="convergence_test", ctype=CommandType.PRE_EXPANSION, returnValue=False)
def _get_convergence_test_key(config=None, key=None, value=None, pipecommands=""):
    config["__CONVERGENCE_TEST.__test_key"] = key
    if not "__output_extension" in config:
        config["__output_extension"] = "output"

    if "expand" in pipecommands:
        config[key] = value + pipecommands
    else:
        config[key] = value + "| expand" + pipecommands
