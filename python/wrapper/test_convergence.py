from parseIni import parse_ini_file
from metaIni import expand_meta_ini, parse_meta_ini_file, write_configuration_to_ini
from convergencetest_metaini import extract_convergence_test_info
import os
import sys
from math import log

def call(metaini):
    # get the convergence test info from the meta ini file
    testKeyDict = expand_meta_ini(metaini, filterKeys="__CONVERGENCE_TEST.TestKey", addNameKey=False)
    testKey = testKeyDict[0]["__CONVERGENCE_TEST.TestKey"]

    # get the convergence tests
    tests = extract_convergence_test_info(metaini)

    # assume we are in the same directory as the test was executed
    # manipulate the __name key accordingly
    for test in tests:
        for run in test:
            run["__name"] = os.path.basename(run["__name"])

    output = []
    # read the outputted data in a dict
    for testIdx, test in enumerate(tests):
        output.append([])
        for run in test:
            # TODO specify the extension in the metaini file
            outDict = parse_ini_file(run["__name"] + ".output")
            outDict["testKey"] = run[testKey]
            outDict["expectedRate"] = run["__CONVERGENCE_TEST.ExpectedRate"]
            outDict["eps"] = run["__CONVERGENCE_TEST.AbsoluteDiff"]
            output[testIdx].append(outDict)

    test_failed = False
    # calculate the rate according to the outputted data

    def to_float(dqstring):
        from ast import literal_eval
        return float(literal_eval(dqstring))

    for testIdx, test in enumerate(tests):
        for runIdx in range(len(test)-1):
            norm1 = to_float(output[testIdx][runIdx]["Norm"])
            norm2 = to_float(output[testIdx][runIdx+1]["Norm"])
            hmax1 = to_float(output[testIdx][runIdx]["HMax"])
            hmax2 = to_float(output[testIdx][runIdx+1]["HMax"])
            rate = log(norm2/norm1)/log(hmax2/hmax1)
            # compare the rate to the expected rate
            if abs(rate-to_float(output[testIdx][runIdx]["expectedRate"])) > to_float(output[testIdx][runIdx]["eps"]):
                test_failed = True
                sys.stderr.write("Test failed because the absolute difference between the \
                    calculated rate: " + str(rate) + " and the expected rate: " + \
                    output[testIdx][runIdx]["expectedRate"] + " was too large.\n")

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
    args = vars(parser.parse_args())

    sys.exit(call(args["ini"]))
