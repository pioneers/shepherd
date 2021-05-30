"""
This file runs the tests in the tests folder and exits with code 0 on success.
This will be used by Travis.
"""
import os
from os import DirEntry
from subprocess import Popen, PIPE
import sys
import time
# pylint: disable = global-statement
SUCCESS = True

instruction_file = "instructions.shepherd"

def run_test(name, path, verbose=False):
    '''
    Reads the instructions file and runs each test in the order specified by the instructions.
    Waits until the first process fails or until all TEST processes succesfully exit.

    There is a 0.1 second delay between each process to ensure that the order is maintained.
    If you are encountering an infinite loop, try changing this delay
    as well as ensuring that your instructions are in a valid order.

    A 5 second delay is added after any REAL file is run, to ensure startup. If
    this still results in an infinite loop, consider adding a SLEEP statement to
    the begining of all your TEST files for additional delay.
    '''
    global SUCCESS
    print(f"[STARTING] {name}")
    instructions = open(os.path.join(
        path, 'instructions.shepherd'), "r")
    files = list(map(lambda s: s.strip().split(" "), instructions))
    test_processes = []
    real_processes = []
    for type, file in files:
        if type == "REAL":
            args = ['python3', file]
        elif type == "TEST":
            args = ['python3', 'Tester.py', os.path.join(name, file)]
        else:
            raise Exception(f"did not recognize test type {type}")
        if type == "REAL":
            real_processes.append(Popen(args, stdout=sys.stdout if verbose else PIPE))
            time.sleep(5)
        elif type == "TEST":
            test_processes.append(Popen(args, stdout=sys.stdout if verbose else PIPE))
            time.sleep(0.1)
    passed = True
    done = False
    while not done:
        done = True
        for process in test_processes:
            poll = process.poll()
            if poll is None:
                done = False
            elif poll != 0:
                passed = False
    if passed:
        print(f"[PASSED] {name}")
    else:
        print(f'one or more processes errored when running {name}')
        print(f"[FAILED] {name}")
        SUCCESS = False
    print("---------------\n")
    for process in real_processes:
        process.kill()

def start():
    """
    Process argv and run as many applicable tests. This could be all tests,
    a group of tests, or a specific test.

    If -h or -help is present in the list of args, run no tests and instead
    print out a list of all possible tests.
    """
    # collect all valid tests and test groups
    tentative_test_groups = [f.name for f in filter(lambda f: f.is_dir(), os.scandir('./tests'))]
    test_groups = {}
    tests = []
    for test_group in tentative_test_groups:
        tentative_tests = [f for f in filter(lambda f: f.is_dir(), os.scandir(os.path.join('./tests', test_group)))]
        local_tests = []
        for test in tentative_tests:
            if os.path.exists(os.path.join(test, instruction_file)):
                test = os.path.join(test_group, test.name)
                local_tests += [test]
                tests += [test]
        if local_tests:
            test_groups[test_group] = local_tests

    queued_tests = []
    # queue the specified tests:
    if len(sys.argv) >= 2:
        # check for help flag
        if "-h" in sys.argv[1:] or "-help" in sys.argv[1:]:
            print("testing_script.py takes any number of the following arguments:")
            print("leave args empty to run all tests.")
            print("  to run test groups:")
            for test_group in test_groups.keys():
                print(f"    {test_group}")
            print("  to run individual tests:")
            for test in tests:
                print(f"    {test}")
            print("  to bring up the help menue:")
            print("    -help")
            print("    -h")
            sys.exit(-1)
        else:
            for test in sys.argv[1:]:
                # check if the specified test was a test group
                if test in list(test_groups.keys()):
                    for t in test_groups[test]:
                        #no duplicates
                        if not t in queued_tests:
                            queued_tests += [t]
                # check if the specified test was a single test
                elif test in tests:
                    #no duplicates
                    if not test in queued_tests:
                        queued_tests += [test]
                # an invalid test was passed in
                else:
                    print(f"Invalid test: {test}. Use -help to see a list of tests.")
                    sys.exit(-1)
    # otherwise, queue all tests
    else:
        queued_tests = tests

    # and now run them
    print(f"Running {len(queued_tests)} out of {len(tests)} possible tests")
    print("---------------\n")
    for test in queued_tests:
        run_test(test, os.path.join('./tests', test), verbose=True)

    if SUCCESS:
        print("[PASSED ALL TESTS]")
        sys.exit(0)
    else:
        print("[DID NOT PASS ALL TESTS]")
        sys.exit(-1)

if __name__ == '__main__':
    start()
