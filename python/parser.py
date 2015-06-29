""" Define a parser from EBNF for the meta ini syntax """

from pyparsing import Literal, printables, Word, Optional, restOfLine, ZeroOrMore, Group
from dotdict import DotDict

# Constructing parser objects might be costly... keep a cache!
_ini_bnf_cache = {}

def ini_bnf(assignment="=", commentChar="#"):
    """ The EBNF for a normal Dune style ini file. """
    if (assignment, commentChar) not in _ini_bnf_cache:
        lbrack = Literal("[").suppress()
        rbrack = Literal("]").suppress()
        equals = Literal(assignment).suppress()
        comm = Literal(commentChar).suppress()

        # A comment starts with the comment literal and affects the rest of the line
        comment = comm + Optional(restOfLine).suppress()
        # A section is guarded bz square brackets
        section = lbrack + Word(printables, excludeChars=["]"]) + rbrack
        # A key can consist of anything that is not an equal sign
        key = Word(printables, excludeChars="=")
        # A value may contain virtually anything
        value = Word(printables + " ", excludeChars=commentChar)
        # A key value pair is a concatenation of those 3
        keyval = key + equals + value
        # Introduce the include statement here, although I do like it anymore.
        include = (Literal("include") | Literal("import")).setParseAction(lambda x : "__include") + Word(printables, excludeChars=commentChar)

        line = comment | (keyval | section | include) + Optional(comment)

        _ini_bnf_cache[(assignment, commentChar)] = ZeroOrMore(Group(line))

    return _ini_bnf_cache[(assignment, commentChar)]

def parse_ini_file(filename, assignment="=", commentChar="#"):
    """ Take an inifile and parse it into a DotDict """
    # Get an EBNF parser and apply it!
    bnf = ini_bnf(assignment=assignment, commentChar=commentChar)
    parseresult = bnf.parseFile(filename)

    # Initialize an empty return dict and a working dict for subgrouping
    result_dict = DotDict()
    current_dict = result_dict
    for part in parseresult:
        if len(part) == 1:
            if not part[0] in result_dict:
                result_dict[part[0]] = DotDict()
            current_dict = result_dict[part[0]]
        if len(part) == 2:
            if part[0] == '__include':
                import os.path
                incfile = os.path.join(os.path.dirname(filename), part[1])
                other = parse_ini_file(incfile, assignment=assignment, commentChar=commentChar)
                for key, val in other.items():
                    result_dict[key] = val
            else:
                current_dict[part[0]] = part[1].strip()

    return result_dict

# Constructing parser objects might be costly... keep a cache!
_metaini_bnf_cache = {}

def metaini_bnf(commentChar="#"):
    """ The EBNF for the extensions to the ini format we do allow """
    if (commentChar,) not in _metaini_bnf_cache:
        comm = Literal(commentChar).suppress()
        comment = comm + Optional(restOfLine).suppress()
        cmdname = Word(printables + " ", excludeChars="#") + Optional(comment)
        command = comm + comm + cmdname
        _metaini_bnf_cache[(commentChar,)] = ZeroOrMore(command)

    return _metaini_bnf_cache[(commentChar,)]
