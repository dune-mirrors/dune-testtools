from metaIni import expand_meta_ini, parse_meta_ini_file, write_configuration_to_ini
from writeIni import write_dict_to_ini
from static_metaini import extract_static_info
from cmakeoutput import printForCMake
import argparse
import sys

def extract_convergence_test_info(metaini):
    # get the key that will define the convergence test
    testKeyDict = expand_meta_ini(metaini, filterKeys="__CONVERGENCE_TEST.TestKey", addNameKey=False)
    
    # if no __CONVERGENCE_TEST.TestKey was found exit with parameter error message
    if len(testKeyDict[0]) == 0:
        sys.stderr.write("Parameter Error: __CONVERGENCE_TEST section has no key 'TestKey': in meta-inifile: " + str(metaini) + "\n")
        sys.exit(0)
    # if somebody tries expansion assignment operators on the TestKey throw a parameter error as
    # this option is not really useful. Time and space convergence e.g. can be done with two separate inifiles.
    if len(testKeyDict) > 1:
        sys.stderr.write("Parameter Error: The '__CONVERGENCE_TEST.TestKey' has to be a single key: in meta-inifile: " + str(metaini) + "\n")
        sys.exit(0)

    # this is the test key
    testKey = testKeyDict[0]["__CONVERGENCE_TEST.TestKey"]
       
    # check if the given testKey exists
    testKeyDict = expand_meta_ini(metaini, filterKeys=testKey, addNameKey=False)
    if len(testKeyDict[0]) == 0:
        sys.stderr.write("Parameter Error: The given 'TestKey': " + str(testKey) + " does not match any key in the meta-inifile: " + str(metaini) + "\n")
        sys.exit(0)

    # expand the ini file
    configurations = expand_meta_ini(metaini)

    # some configurations belong to the same convergence test...
    def dict_is_equal_except(d1, d2, keys=[]):
        isEqual = True
        if type(keys) is not list:
            keys = [keys]
        for key, value in d1.items():
            if key in d2:
                if key not in keys and not d2[key]==value:
                    isEqual = False
            else:
                isEqual = False
        return isEqual

    # parse the meta ini file
    normal, result = parse_meta_ini_file(metaini)

    # which keys depend on the testkey?
    dependentKeys = [testKey]
    for key, value in normal.items():
    	if testKey in value:
    		dependentKeys.append(key)
    for char, assignType in result.items():
        for key, value in assignType.items():
    		if testKey in value:
    			dependentKeys.append(key)

    # ...aggregate those into groups
    newconfigurations = []
    count = 0
    visited = [False for i in range(len(configurations))]

    for idx, c in enumerate(configurations):
        if not visited[idx]:
            newconfigurations.append([c])
            count = count + 1
            visited[idx] = True
            # check for confs in the same convergence test run
            for idx2, c2 in enumerate(configurations):
                if not visited[idx2]:
                    if dict_is_equal_except(c, c2, dependentKeys):
                        newconfigurations[count-1].append(c2)
                        visited[idx2] = True

    # check if we have the right number of convergence tests
    assert(count == len(newconfigurations))

    return newconfigurations

if __name__ == "__main__":
    # read command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    parser.add_argument('-d', '--dir', help='The directory to put the output in')
    parser.add_argument('-c', '--cmake', action="store_true", help='Set if the script is called from cmake and should return data to it')
    args = vars(parser.parse_args())

    # extract the convergence tests
    configurations = extract_convergence_test_info(args["ini"])

     # extract the static information from the meta ini file
    static_info = extract_static_info(args["ini"])

    # initialize a data structure to pass the list of generated ini files to cmake
    metaini = {}
    metaini["names"] = []  # TODO this should  have underscores!
    metaini["tests"] = []

    for index, test in enumerate(configurations):
        # write out the list of tests
        metaini["tests"].append(str(index))
        # write the configurations to the file specified in the name key.
        for c in test:
            write_configuration_to_ini(c, metaini, static_info, args, str(index) + "_")

    if args["cmake"]:
        printForCMake(metaini)
