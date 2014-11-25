""" define tools for parsing Dune-style ini files into python

TODO:
- allow values to be lists (as pntained by Dune::FieldVector)
- improve the group key detection
"""

# inspired by http://www.decalage.info/fr/python/configparser

def parse_ini_file(filename, commentChar = ("#",), assignChar=("=",":"), asStrings=True, conversionList=(int, float,)):
    """ parse Dune style .ini files into a dictionary
       
    The parser behaviour can be customized by the keyword arguments of this function.
    The dictionary contains nested dictionaries according to nested subgroups in the
    ini file.
        
    Keyword arguments:
    ------------------
    commentChar: list
        A list of characters that define comments. Everything on a line
        after such character is ignored during the parsing process.
    assignChar : list
        A list of characters that separates the key from the value on a line 
        containing a key/value pair.
    asStrings : bool
        Whether the values should be treated as strings. At the moment, this
        defaults to true (until better stuff is implemented)
    conversionList : list 
        A list of functions to try for converting the parsed strings to other types
        The order of the functions defines the priority of the conversion rules
        (highest priority first). All conversion rules are expected to raise
        a ValueError when they are not applicable.
    """
    result_dict = {}
    f = open(filename)
    current_dict = result_dict
    for line in f:
        # strip the endline character
        line = line.strip("\n")
            
        # strip comments from the line
        for char in commentChar:
            if char in line:
                line, comment = line.split(char, 1)        
            
        # check whether this line specifies a group
        # TODO allow keys to contain a "[" too
        if "[" in line:
            # reset the current dictionary
            current_dict = result_dict
       
            # isolate the group name
            group, bracket = line.split("]", 1)
            bracket, group = group.split("[", 1)
            group = group.strip(" ")

            # process the stack of subgroups given
            while "." in group:
                subgroup, group = group.split(".", 1)
                current_dict[subgroup] = {}
                current_dict = current_dict[subgroup]
                 
            # add a new dictionary for the group name and set the current dict to it
            current_dict[group] = {}
            current_dict = current_dict[group]
            
        # check whether this line defines a key
        for char in assignChar:
            if char in line:
                print "Line with a key/value pair: {}".format(line)
                
                # split key from value
                key, value = line.split(char, 1)
                
                # strip blanks from the value 
                value = value.strip()
                 
                # set the dictionary entry for this pair to the default string
                current_dict[key] = value
                     
                # check whether a given conversion applies to this key
                if not asStrings:
                    # iterate over the list of conversion functions in reverse priority order
                    for rule in [x for x in reversed(conversionList)]:
                        try:
                            current_dict[key] = rule(value)
                        except ValueError:
                            pass
                        
    return result_dict
        
