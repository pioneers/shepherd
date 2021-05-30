"""
This file runs the tests in the tests folder and exits with code 0 on success.
This will be used from Travis.
"""
import os
from os import DirEntry
from subprocess import Popen, PIPE
import sys
import time
# pylint: disable = global-statement
SUCCESS = True


def run_test(name, path, verbose=False):
    '''
    Reads the instructions file and runs each test in the order specified by the instructions.
    Waits until the first process fails or until all processes succesfully exit.

    There is a 0.1 second delay between each process to ensure that the order is maintained.
    If you are encountering an infinite loop, try changing this delay
    as well as ensuring that your instructions are in a valid order.
    '''
    global SUCCESS
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
        print(f"PASSED {name}")
    else:
        print(f'one or more processes errored when running {name}')
        print(f"FAILED {name}")
        SUCCESS = False
    print("---------------\n")
    for process in real_processes:
        process.kill()


# run the specified tests if specified or run all tests
if len(sys.argv) >= 2:
    for test in sys.argv[1:]:
        run_test(test, os.path.join('./tests', test), verbose=True)
else:
    f: DirEntry
    for f in filter(lambda f: f.is_dir(), os.scandir('./tests')):
        run_test(f.name, f.path, verbose=True)

if SUCCESS:
    print("PASSED ALL TESTS")
    sys.exit(0)
else:
    print("DID NOT PASS ALL TESTS")
    sys.exit(-1)
