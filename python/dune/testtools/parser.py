""" Define a parser from EBNF for the meta ini syntax """
from __future__ import absolute_import
from __future__ import print_function

from pyparsing import Literal, Word, alphanums, Combine, OneOrMore, ZeroOrMore, QuotedString, Optional, restOfLine, printables, oneOf, Group, LineEnd
from collections import namedtuple
import os.path
from dune.testtools.parametertree.dotdict import DotDict

CommandToApply = namedtuple('CommandToApply', ['name', 'args', 'key'])


class MetaIniParser(object):
    # Define a switch for logging information. This is very useful debugging the parser.
    _logging = False

    def __init__(self, assignment="=", commentChar="#", path=""):
        self._path = path
        self._counter = 0
        self._currentGroup = ''
        self._currentDict = DotDict()

        # To avoid cyclic dependencies, we do NOT do this import in the module header
        from dune.testtools.command import command_registry, CommandType, command_count
        self._foundCommands = {i: [] for i in range(command_count())}
        self._commands = " ".join(command_registry())
        self._parser = self.construct_bnf(assignment=assignment, commentChar=commentChar)

    def log(self, s):
        if MetaIniParser._logging:
            print(s)

    def construct_bnf(self, assignment="=", commentChar="#"):
        """ The EBNF for a normal Dune style ini file. """
        # A comment starts with the comment literal and affects the rest of the line
        comment = Literal(commentChar).suppress() + Optional(restOfLine).suppress()
        # A section is guarded by square brackets
        section = Literal("[") + Word(alphanums + "._").setParseAction(self.setGroup) + Literal("]")
        # A key can consist of anything that is not an equal sign
        key = Word(alphanums + "_.")
        # define a command
        command = Group(Literal("|").suppress() + oneOf(self._commands) + ZeroOrMore(Word(alphanums + "_{}", excludeChars=[commentChar, "|"])))
        # A value may contain virtually anything
        value = Combine(OneOrMore(QuotedString(quoteChar='"', escChar='\\').setParseAction(self.escapeQuoted) | Word(printables + " ", excludeChars=[commentChar, '"', "|"])))
        # A key value pair is a concatenation of those 3
        keyval = (key + Literal(assignment).suppress() + value + ZeroOrMore(command)).setParseAction(self.setKeyValuePair)
        # We allow reading data, that is not of key/value pair form
        # We do lose the embeddedness of our language at this point.
        # An alternative would be to place commands behind ## directive.
        nonkeyval = (value + OneOrMore(command)).setParseAction(self.setNonKeyValueLine)
        # Introduce the include statement here, although I do like it anymore.
        include = oneOf("include import") + Word(printables, excludeChars=commentChar).setParseAction(self.processInclude)
        # Define the priority between the different sorts of lines. Important: keyval >> nonkeyval
        content = keyval | section | include | nonkeyval
        line = Optional(content) + Optional(comment) + LineEnd()

        return line

    def escapeQuoted(self, origString, loc, tokens):
        self.log("Going to escape {}".format(tokens[0].strip()))
        for char in ",|":
            tokens[0] = tokens[0].replace(char, "\\" + char)

    def setGroup(self, origString, loc, tokens):
        self.log("Setting current group from '{}' to '{}.'".format(self._currentGroup, tokens[0].strip()))
        self._currentGroup = tokens[0] + "."

    def setKeyValuePair(self, origString, loc, tokens):
        self.log("Setting KV pair ('{}', '{}') within group '{}'".format(tokens[0].strip(), tokens[1].strip(), self._currentGroup))
        # store the key value pair for the return dictionary
        self._currentDict[self._currentGroup + tokens[0].strip()] = tokens[1].strip()
        # store the found commands
        for command in tokens[2:]:
            self.log("  with an applied command: '{}'".format(command))
            commandtuple = CommandToApply(command[0], command[1:], self._currentGroup + tokens[0].strip())
            from dune.testtools.command import command_registry
            self._foundCommands[command_registry()[command[0]]._ctype].append(commandtuple)

    def setNonKeyValueLine(self, origString, loc, tokens):
        self.log("Setting Non-KV line: {}".format(tokens[0].strip()))
        # store the given value under a special section
        self._currentDict['__local.conditionals.' + str(self._counter)] = tokens[0].strip()
        # store the found commands
        for command in tokens[1:]:
            self.log("  with an applied command: '{}'".format(command))
            commandtuple = CommandToApply(command[0], command[1:], '__local.conditionals.' + str(self._counter))
            from dune.testtools.command import command_registry
            self._foundCommands[command_registry()[command[0]]._ctype].append(commandtuple)
        # increase the counter
        self._counter = self._counter + 1

    def processInclude(self, origString, loc, tokens):
        self.log("Processing include directive from {}".format(tokens[0].strip()))
        self._currentGroup = ''
        # Parse the include
        incfile = open(os.path.join(self._path, tokens[0]), "r")
        for line in incfile:
            self.apply(line)
        # Reset current File and group
        self._currentGroup = ''

    def apply(self, line):
        self.log("Parsing line: {}".format(line))
        self._parser.parseString(line)

    def result(self):
        return (self._currentDict, self._foundCommands)


# This is backwards compatibility, we could as  well skip it.
def parse_ini_file(filename, assignment="=", commentChar="#", returnCommands=False):
    """ Take an inifile and parse it into a DotDict """
    parser = MetaIniParser(assignment=assignment, commentChar=commentChar, path=os.path.dirname(filename))
    file = open(filename, "r")
    for line in file:
        parser.apply(line)
    if returnCommands:
        return parser.result()
    else:
        return parser.result()[0]
