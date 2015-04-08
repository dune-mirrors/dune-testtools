from metaIni import expand_meta_ini, write_configuration_to_ini
from parseIni import *
from writeIni import write_dict_to_ini

from command import meta_ini_command, CommandType
from escapes import *
from static_metaini import extract_static_info

from cmakeoutput import printForCMake
import argparse
import sys

def extract_convergence_test_info(metaini):
    # get the key that will define the convergence test
    testKeyDict = expand_meta_ini(metaini, whiteFilter="__CONVERGENCE_TEST.__test_key", addNameKey=False)
    
    # if no __CONVERGENCE_TEST.TestKey was found exit with parameter error message
    if len(testKeyDict[0]) == 0:
        sys.stderr.write("Parameter Error: No key was marked as test key with the '| convergence_test' command : in meta-inifile: " + str(metaini) + "\n")
        sys.exit(0)

    # this is the test key
    testKey = testKeyDict[0]["__CONVERGENCE_TEST.__test_key"]

    # parse the meta ini file
    parse = parse_ini_file(metaini)

    # which keys depend on the testkey
    # the __name value is always unique and should be included from comparison
    dependentKeys = [testKey, "__name"]
    # do it as long as no resolution is need anymore
    # values can depend on keys that depend on other keys arbitrarily deep
    def get_dependent_keys(parse, dependentKeys):
        needs_resolution = False
        for key, value in parse.items():
           for dependentKey in dependentKeys:
                if exists_delimited(str(value), dependentKey) and key not in dependentKeys:
                    dependentKeys.append(key)
                    needs_resolution = True
        return needs_resolution

    # check the parse dictionary for key dependencies
    valuelist = escaped_split(parse[testKey], delimiter=",")
    for value in valuelist:
        if exists_unescaped(value, "{") or exists_unescaped(value, "}"):
            resultkey = extract_delimited(value, leftdelimiter="{", rightdelimiter="}")
            if exists_unescaped(resultkey, "{") or exists_unescaped(resultkey, "}"):
                sys.stderr.write("Nested key names currently not supported for the convergence test key.")
                sys.exit(1)
            else:
                if resultkey not in dependentKeys:
                    dependentKeys.append(resultkey)

    # then we resolve all other dependent keys
    while get_dependent_keys(parse, dependentKeys): pass

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
