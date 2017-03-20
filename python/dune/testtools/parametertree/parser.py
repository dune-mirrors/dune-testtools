""" Define a parser from EBNF for the Dune Style ini file syntax """
from __future__ import absolute_import
from __future__ import print_function

from pyparsing import *
from dune.testtools.parametertree.dotdict import DotDict


class DuneIniParser(object):
    # Define a debug logging switch
    _debug = False

    def __init__(self, assignment="=", commentChar="#"):
        self._currentGroup = ''
        self._result = DotDict()
        self._parser = self.construct_bnf(assignment=assignment, commentChar=commentChar)

    def log(self, s):
        if DuneIniParser._debug:
            print(s)

    def construct_bnf(self, assignment="=", commentChar="#"):
        """ The EBNF for a normal Dune style ini file. """
        # A comment starts with the comment literal and affects the rest of the line
        comment = Literal(commentChar).suppress() + Optional(restOfLine).suppress()
        # A section is guarded by square brackets
        section = Literal("[") + Word(alphanums + "._").setParseAction(self.setGroup) + Literal("]")
        # A key can consist of anything that is not an equal sign
        key = Word(alphanums + "-_.")
        # A value may contain virtually anything
        value = Word(printables + " ", excludeChars=[commentChar])
        # A key value pair is of the form 'key=value'
        keyval = (key + Literal(assignment).suppress() + value).setParseAction(self.setKeyValuePair)
        # Define the priority between the different sorts of lines.
        content = keyval | section
        # Define a line
        line = Optional(content) + Optional(comment) + LineEnd()

        return line

    def setGroup(self, origString, loc, tokens):
        self.log("Setting current group from '{}' to '{}.'".format(self._currentGroup, tokens[0].strip()))
        self._currentGroup = tokens[0] + "."

    def setKeyValuePair(self, origString, loc, tokens):
        self.log("Setting KV pair ('{}', '{}') within group '{}'".format(tokens[0].strip(), tokens[1].strip(), self._currentGroup))
        # store the key value pair for the return dictionary
        self._result[self._currentGroup + tokens[0].strip()] = tokens[1].strip()

    def apply(self, filename):
        self.log("Parsing file: {}".format(filename))
        f = open(filename, "r")
        for line in f:
            self.log("Parsing line: {}".format(line))
            self._parser.parseString(line)

        return self._result


def parse_ini_file(filename):
    return DuneIniParser().apply(filename)
