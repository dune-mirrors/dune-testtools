""" A module for expanding meta ini files into sets of ini files.

TODO: Write a documentation on the format.

TODO
- Is it too restrictive to forbid assignment chars in keys and values?
- Implement key-dependent values, like
    vtkfile = refinement{grid.level}.vtk
- Reserve a __name key as an alternative to consecutive numbering
- Fixsubgroup notation in the main parser: group definitions dont require the
entire stack of groups but only dots for the tree depth 
"""

from parseIni import parse_ini_file
from copy import deepcopy

def write_dict_to_ini(d, filename):
    with open(filename,'w') as f:
                        
        def traverse_dict(file, d, depth):
            # first traverse all non-group values (they would otherwise be considered part of a group)
            for key, value in d.items():
                if type(value) is not dict:
                    file.write("{} = {}\n".format(key, value))
                    
            # now go into subgroups
            for key, value in d.items():
                if type(value) is dict:
                    file.write("[{}{}]\n".format('.'*depth,key))
                    traverse_dict(file, value, depth+1)
        
        traverse_dict(f, d, 0)
        
                
def expand_meta_ini(filename):
    """ take a meta ini file and construct the set of ini files it defines
    
    Arguments:
    ----------
    filename : string
        The filename of the meta ini file
    """
    
    # one dictionary to hold the results from several parser runs
    # the keys are all the types of assignments occuring in the file
    # except for normal assignment, which is treated differently. 
    result = {}
    
    # we always have normal assignment
    normal = parse_ini_file(filename)
    
    # look into the file to determine the set of assignment operators used
    file = open(filename)
    for line in file:
        if line.count("=") is 2:
            key, assignChar, value = line.split("=")
            result[assignChar] = {}
    
    # get dictionaries for all sorts of assignments
    for key in result:
        assignChar = "={}=".format(key)
        result[key] = parse_ini_file(filename, assignment=assignChar)
        
    # start combining dictionaries - there is always the normal dict
    configurations = [normal]
    
    def generate_configs(d,configurations,prefix=[]):
        
        def configs_for_key(key,vals,configs,prefix):
            for config in configs:
                for val in vals:
                    c = deepcopy(config)
                    pos = c
                    for p in prefix:
                        pos = pos[p]
                    pos[key] = val
                    yield c
        
        for key,values in d.items():
            if type(values) is dict:
                pref = prefix + [key]
                configurations = generate_configs(values, configurations,pref)
            else:
                values = [v.strip() for v in values.split(',')]
                configurations = configs_for_key(key,values,configurations,prefix)
            
        for config in configurations:
            yield config
    
    # do the all product part associated with the == assignment
    if "" in result:
        configurations = [l for l in generate_configs(result[""], configurations)]
        
    print "Configs: "
    for c in configurations:
        print c
            
    def expand_dict(d, output = None, prefix=[]):
        
        for key,values in d.items():
            if type(values) is dict:
                pref = prefix + [key]
                output = expand_dict(values, output, pref)
            else:
                values = [v.strip() for v in values.split(',')]
                if output is None:
                    output = [{} for i in range(len(values))] 
                for index, val in enumerate(values):
                    mydict = output[index]
                    for p in prefix:
                        if p not in mydict:
                            mydict[p] = {}
                        mydict = mydict[p]
                    mydict[key] = val
                    
        return output
    
    def join_nested_dicts(d1, d2):
        for key,item in d2.items():
            if type(item) is dict:
                d1[key] = join_nested_dicts(d1[key], item)
            else:
                d1[key] = item
        return d1
                    
    # do the part for all other assignment operators
    for assign, tree in result.items():
        # ignore the one we already did above
        if assign is not "":
            expanded_dict = expand_dict(tree)
            
            newconfigurations = []
            
            # combine the expanded dictionaries with the ones in configurations
            for config in configurations:
                for newpart in expanded_dict:
                    #newconfigurations.append(dict(config.items() + newpart.items()))
                    newconfigurations.append(join_nested_dicts(deepcopy(config), newpart))
            
            configurations = newconfigurations
            
    print "Configs: "
    for c in configurations:
        print c
    
    # resolve all key-dependent names
    # TODO
    
    # write the configurations
    counter = 0
    base, extension = filename.split(".", 1)
    for conf in configurations:
        conffile = base + str(counter)
        counter = counter + 1
        write_dict_to_ini(conf, conffile)