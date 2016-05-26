#!/usr/bin/env python

"""
An analysis script for checking validity of meta ini files
and inspecting the resulting configuration upon expansion.

Because all Python code in ``dune-testtools`` runs in a virutalenv
by default running the analysis script is not straight forward. Luckily,
it's not too hard either. Analyse your favorite meta ini file with

.. code-block:: shell

    ./<build directory>/dune-env dune_metaini_analysis.py <path to ini file>

from the top level project directory. The analysis script will inform you on
any detected irregularities in your meta ini files. Given that the expansion
process was successful, you can interactively step through the resulting
ini files.

"""
if __name__ == "__main__":

    from dune.testtools.metaini import expand_meta_ini
    from dune.testtools.parser import parse_ini_file, MetaIniParser
    from dune.testtools.writeini import write_to_stream
    import argparse
    import sys
    import os

    # Python 2/3 compatibility
    try:
        input = raw_input
    except NameError:
        pass

    def check_parser(ini):
        try:
            parsed = parse_ini_file(ini)
        except:
            try:
                file = open(ini, "r")
            except:
                print("Reading the source file failed. Did you give a correct path?")
                sys.exit(1)
            print("Parsing the meta ini file failed.")
            print("Now attempting to find lines that cannot be parsed.")
            parser = MetaIniParser(path=os.path.dirname(ini))
            for line in file:
                try:
                    parser.apply(line)
                except:
                    print("ERROR Malformed line: '{}'".format(line))
                    # TODO give some info about how its malformed: Needs inspection of the exception.
            sys.exit(1)

        # If we got until here, the file could be parsed correctly
        print("Parsing the ini file was successful...")
        return parsed

    def check_misusage(ini):
        # Check some common misusage patterns:
        for k, v in ini.items():
            if v[0] == "=":
                print("WARNING: '{}={}' parsed as key-value-pair. Use double quotes to enforce a conditional.".format(k, v))

    def check_expansion(ini):
        # Now try doing the expansion and output some statistics:
        try:
            exp = expand_meta_ini(ini)
        except Exception as e:
            print(e)
            print("Expanding the meta ini file failed.")
            # TODO comma separated lists with non-matching length?
            print("Please submit a bug report via http://conan2.iwr.uni-heidelberg.de/git/dominic/dune-testtools or via mail")
            sys.exit(1)

        print("Expanding the ini file was successful and yielded {} configurations...".format(len(exp)))
        return exp

    def inspect_interactive(configs):
        inputKey = ""
        current = 0
        while inputKey != "q":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Showing configuration {} of {}:\n".format(current, len(configs)))
            write_to_stream(configs[current], sys.stdout)
            print("\n\nWhat to do now?")
            print("n: Show next configuration")
            print("p: Show previous configuration")
            print("f: Show first configuration")
            print("q: quit")
            print("\nYour choice (confirm with enter): ")

            inputKey = input().lower()
            if inputKey == "n":
                current = (current + 1) % len(configs)
            if inputKey == "p":
                current = (current - 1) % len(configs)
            if inputKey == "f":
                current = 0

    def analysis(ini, interactive=False):
        parsed = check_parser(ini)
        check_misusage(parsed)
        configs = check_expansion(ini)
        print("\nDo you want to interactively inspect the expanded configurations? [y/n]")
        if interactive or input().lower() == "y":
            inspect_interactive(configs)

    # define the argument parser for this script
    parser = argparse.ArgumentParser()
    parser.add_argument('inifile', type=str, nargs=1)
    parser.add_argument('-i', '--interactive', action="store_true", help="Whether to interactvely investigate the data")
    args = vars(parser.parse_args())
    analysis(args['inifile'][0], interactive=args['interactive'])
