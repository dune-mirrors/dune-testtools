""" Define a parser from EBNF for the meta ini syntax """

from pyparsing import Literal, Word, alphanums, Combine, OneOrMore, ZeroOrMore, QuotedString, Optional, restOfLine, printables, oneOf, Group, LineEnd
from dotdict import DotDict
import os.path

class MetaIniParser(object):
    # Define a switch for logging information. This is very useful debugging the parser.
    _logging = False

    def __init__(self, assignment="=", commentChar="#", path=""):
        self._path = path
        self._counter = 0
        self._currentGroup = ''
        self._currentDict = DotDict()

        # To avoid cyclic dependencies, we do NOT do this import in the module header
        from command import command_registry
        self._commands = " ".join(command_registry())
        self._parser = self.construct_bnf(assignment=assignment, commentChar=commentChar)

    def log(self, s):
        if MetaIniParser._logging:
            print s

    def construct_bnf(self, assignment="=", commentChar="#"):
        """ The EBNF for a normal Dune style ini file. """
        # A comment starts with the comment literal and affects the rest of the line
        comment = Literal(commentChar).suppress() + Optional(restOfLine).suppress()
        # A section is guarded by square brackets
        section = Literal("[") + Word(alphanums + "._").setParseAction(self.setGroup) + Literal("]")
        # A key can consist of anything that is not an equal sign
        key = Word(alphanums + "_.")
        # define a command
        command = Group(Literal("|").suppress() + oneOf(self._commands) + ZeroOrMore(Word(alphanums, excludeChars=[commentChar, "|"])))
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
        if len(tokens) > 2:
            self.log("Command tokens: '{}'".format(tokens[2:]))
        self._currentDict[self._currentGroup + tokens[0].strip()] = tokens[1].strip()
        # Get an intermediate working stage
        for command in tokens[2:]:
            self._currentDict[self._currentGroup + tokens[0].strip()] = self._currentDict[self._currentGroup + tokens[0].strip()] + " | " + " ".join(command)

    def setNonKeyValueLine(self, origString, loc, tokens):
        self.log("Setting Non-KV line: {}".format(tokens[0].strip()))
        if len(tokens) > 1:
            self.log("Command tokens: '{}'".format(tokens[1:]))
        self._currentDict['__local.conditionals.' + str(self._counter)] = tokens[0].strip()
        # Get an intermediate working stage
        for command in tokens[1:]:
            self._currentDict['__local.conditionals.' + str(self._counter)] = self._currentDict['__local.conditionals.' + str(self._counter)] + " | " + " ".join(command)
        # remove above
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
        return self._currentDict

# This is backwards compatibility, we could as  well skip it.
def parse_ini_file(filename, assignment="=", commentChar="#"):
    """ Take an inifile and parse it into a DotDict """
    parser = MetaIniParser(assignment=assignment, commentChar=commentChar, path=os.path.dirname(filename))
    file = open(filename, "r")
    for line in file:
        parser.apply(line)
    return parser.result()
