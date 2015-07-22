from __future__ import absolute_import
from pyparsing import alphanums, printables, Word, Literal, restOfLine, SkipTo
from dune_testtools.command import meta_ini_command, CommandType


def _grammar(key):
    quoted = Literal("'") + Literal(key) + Literal("'")
    inother = Word(alphanums, exact=1) + Literal(key)
    ignorePattern = inother | quoted
    return SkipTo(key, ignore=ignorePattern) + Literal(key) + restOfLine

_findkey = Word(printables).suppress() + Literal("'").suppress() + Word(alphanums) + Literal("'").suppress() + Word(printables).suppress()


def eval_boolean(s):
    """ evaluate the given string as a boolean expression """
    def comp(s):
        try:
            return eval(s)
        except NameError as e:
            key = _findkey.parseString(e.args[0])[0]
            parts = _grammar(key).parseString(s)
            return comp(parts[0] + "'" + parts[1] + "'" + parts[2])

    return comp(s)


@meta_ini_command(name="exclude", returnConfigs=True)
def _exclude(configs=None, key=None):
    return [c for c in configs if not eval_boolean(c[key])]


@meta_ini_command(name="label", argc=2, argdefaults=[None, "PRIORITY"], returnValue=False)
def _label(config=None, value=None, args=None):
    if eval_boolean(value):
        config["__LABELS." + args[1]] = args[0]
