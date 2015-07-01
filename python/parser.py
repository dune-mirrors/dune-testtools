""" Define a parser from EBNF for the meta ini syntax """

from pyparsing import Literal, Word, alphanums, Combine, OneOrMore, ZeroOrMore, QuotedString, Optional, restOfLine, printables, oneOf
from dotdict import DotDict
import os.path

def escapesInValues():
    """ defines the characters that should be escaped in values """
    return ",{}|#"

class MetaIniParser(object):
    # Define a switch for logging information. This is very useful debugging the parser.
    _logging = False

    def __init__(self, assignment="=", commentChar="#"):
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
        # A value may contain virtually anything
        value = Combine(OneOrMore(QuotedString(quoteChar='"', escChar='\\').setParseAction(self.escapeQuoted) | Word(printables + " ", excludeChars=[commentChar, '"'])))
        # A key value pair is a concatenation of those 3
        keyval = (key + Literal(assignment).suppress() + value).setParseAction(self.setKeyValuePair)
        # We allow reading data, that is not of key/value pair form
        # We do lose the embeddedness of our language at this point.
        # An alternative would be to place commands behind ## directive.
        nonkeyval = Combine(OneOrMore(QuotedString(quoteChar='"', escChar='\\').setParseAction(self.escapeQuoted) | Word(printables + " ", excludeChars=[commentChar, '"']))).setParseAction(self.setNonKeyValueLine)
        # Introduce the include statement here, although I do like it anymore.
        include = oneOf("include import") + Word(printables, excludeChars=commentChar).setParseAction(self.processInclude)

        line = comment | (keyval | section | include | nonkeyval) + Optional(comment)

        return ZeroOrMore(line)

    def escapeQuoted(self, origString, loc, tokens):
        self.log("Going to escape {}".format(tokens[0]))
        for char in ",|":
            tokens[0] = tokens[0].replace(char, "\\" + char)

    def setGroup(self, origString, loc, tokens):
        self.log("Setting current group from '{}' to '{}.'".format(self._currentGroup, tokens[0]))
        self._currentGroup = tokens[0] + "."

    def setKeyValuePair(self, origString, loc, tokens):
        self.log("Setting KV pair ({}, {}) within group {}".format(tokens[0], tokens[1], self._currentGroup))
        self._currentDict[self._currentGroup + tokens[0]] = tokens[1].strip()

    def setNonKeyValueLine(self, origString, loc, tokens):
        self.log("Setting Non-KV line: {}".format(tokens[0]))
        self._currentDict['__local.conditionals.' + str(self._counter)] = tokens[0].strip()
        self._counter = self._counter + 1

    def processInclude(self, origString, loc, tokens):
        self.log("Processing include directive from {}".format(tokens[0]))
        # save the current file before going into recursion
        file = self._currentFile
        self._currentFile = os.path.join(os.path.dirname(self._currentFile), tokens[0])
        self._currentGroup = ''
        # Parse the include
        self._parser.parseFile(self._currentFile)
        # Reset current File and group
        self._currentGroup = ''
        self._currentFile = file

    def apply(self, filename):
        self._counter = 0
        self._currentGroup = ''
        self._currentDict = DotDict()
        self._currentFile = filename

        self._parser.parseFile(filename)
        return self._currentDict

# This is backwards compatibility, we could as  well skip it.
def parse_ini_file(filename, assignment="=", commentChar="#"):
    """ Take an inifile and parse it into a DotDict """
    return MetaIniParser(assignment=assignment, commentChar=commentChar).apply(filename)