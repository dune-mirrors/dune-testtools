from metaIni import expand_meta_ini, parse_meta_ini_file, write_configuration_to_ini
from escapes import *
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

    # which keys depend on the testkey
    # the __name value is always unique and should be included from comparison
    dependentKeys = [testKey, "__name"]
    # do it as long as no resolution is need anymore
    # values can depend on keys that depend on other keys arbitrarily deep
    def get_dependent_keys(normal, result, dependentKeys):
        needs_resolution = False
        for key, value in normal.items():
           for dependentKey in dependentKeys:
                if exists_delimited(dependentKey, value) and key not in dependentKeys:
                    dependentKeys.append(key)
                    needs_resolution = True
        for char, assignType in result.items():
            for key, value in assignType.items():
                for dependentKey in dependentKeys:
                    if exists_delimited(dependentKey, value) and key not in dependentKeys:
                        dependentKeys.append(key)
                        needs_resolution = True
        return needs_resolution

    # first we check if the testKey itself is dependent on other keys
    # and include those keys in the dependentKeys
    for char, assignType in result.items():
        if testKey in assignType:
            # then it uses a special assignment operator
            # check if the curly bracket operator is used in the testkey value
            valuelist = escaped_split(assignType[testKey], delimiter=",")
            for value in valuelist:
                if exists_unescaped(value, "{") or exists_unescaped(value, "}"):
                    # in order to get all dependent keys we have to possibly resolve
                    # combinations if the dependent key itself uses a curly bracket operator in its name
                    # TODO e.g. key = {foo{bar}} (if bar == 1, 2 there would be the keys foo1 and foo2)
                    # is not allowed yet, throws an error for nested keys
                    resultkey = extract_delimited(value, leftdelimiter="{", rightdelimiter="}")
                    if exists_unescaped(resultkey, "{") or exists_unescaped(resultkey, "}"):
                        sys.stderr.write("Nested key names currently not supported for the convergence test key.")
                        sys.exit(1)
                    else:
                        if resultkey not in dependentKeys:
                            dependentKeys.append(resultkey)

    # do it for the normal dict too
    if testKey in normal:
        value = normal[testKey]
        if exists_unescaped(value, "{") or exists_unescaped(value, "}"):
            resultkey = extract_delimited(value, leftdelimiter="{", rightdelimiter="}")
            if exists_unescaped(resultkey, "{") or exists_unescaped(resultkey, "}"):
                sys.stderr.write("Nested key names currently not supported for the convergence test key.")
                sys.exit(1)
            else:
                if resultkey not in dependentKeys:
                    dependentKeys.append(resultkey)

    # then we resolve all other dependent keys
    while get_dependent_keys(normal, result, dependentKeys): pass

    # aggregate configuration belonging to one convergence test
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
