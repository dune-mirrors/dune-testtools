from parseIni import parse_ini_file
from metaIni import expand_meta_ini, write_configuration_to_ini
from convergencetest_metaini import extract_convergence_test_info
import os
import sys
from math import log

def call(metaini, testId):
    # the id of the test we are checking
    testIdx = int(testId)

    # get the convergence test info from the meta ini file
    testKeyDict = expand_meta_ini(metaini, filterKeys="__CONVERGENCE_TEST.__test_key", addNameKey=False)
    testKey = testKeyDict[0]["__CONVERGENCE_TEST.__test_key"]

    # get the convergence tests
    tests = extract_convergence_test_info(metaini)

    # assume we are in the same directory as the test was executed
    # manipulate the __name key accordingly
    for run in tests[testIdx]:
        run["__name"] = os.path.basename(run["__name"])

    def strip_quotes(dqstring):
        from ast import literal_eval
        return literal_eval(literal_eval(dqstring))

    output = []
    for run in tests[testIdx]:
        ininame = run["__name"]
        if "__output_extension" in run:
            ininame = ininame + "." + run["__output_extension"]
        else:
            ininame = ininame + ".output"
        # check if the output file exists
        if not os.path.isfile(ininame):
            sys.stderr.write("The output file to process does not exist (" + ininame + ")")
            return 1
        # if it exists parse it
        outDict = parse_ini_file(ininame, conversionList=(int, float, strip_quotes))
        outDict["testKey"] = run[testKey]
        outDict["expectedRate"] = float(run["__CONVERGENCE_TEST.ExpectedRate"])
        outDict["eps"] = float(run["__CONVERGENCE_TEST.AbsoluteDiff"])
        output.append(outDict)

    test_failed = False
    # calculate the rate according to the outputted data
    for runIdx in range(len(tests[testIdx])-1):
        norm1 = output[runIdx]["Norm"]
        norm2 = output[runIdx+1]["Norm"]
        hmax1 = output[runIdx]["HMax"]
        hmax2 = output[runIdx+1]["HMax"]
        rate = log(norm2/norm1)/log(hmax2/hmax1)
        # compare the rate to the expected rate
        if abs(rate-output[runIdx]["expectedRate"]) > output[runIdx]["eps"]:
            test_failed = True
            sys.stderr.write("Test failed because the absolute difference between the \
                calculated rate: " + str(rate) + " and the expected rate: " + \
                str(output[runIdx]["expectedRate"]) + " was too large.\n")

    # return appropriate returncode
    if test_failed:
        return 1
    else:
        return 0

# This is also used as the standard wrapper by cmake
if __name__ == "__main__":
    # Parse the given arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ini', help='The meta-inifile to expand', required=True)
    parser.add_argument('-t', '--test', help='The identifier of the test we are checking', required=True)
    args = vars(parser.parse_args())

    sys.exit(call(args["ini"], args["test"]))
    