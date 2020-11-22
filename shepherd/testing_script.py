"""
This file runs the tests in the tests folder and exits with code 0 on success.
This will be used from Travis.
"""
import os
from os import DirEntry
from subprocess import Popen, PIPE
import sys
import time
# pylint: disable=global-statement
SUCCESS = True


def run_test(folder: DirEntry, verbose=False):
    '''
    Reads the instructions file and runs each test in the order specified by the instructions.
    Waits until the first process fails or until all processes succesfully exit.

    There is a 0.1 second delay between each process to ensure that the order is maintained.
    If you are encountering an infinite loop, try changing this delay
    as well as ensurinng that your instructions are in a valid order.
    '''
    global SUCCESS
    instructions = open(os.path.join(
        folder.path, 'instructions.shepherd'), "r")
    files = list(map(lambda s: s.strip(), instructions))
    processes = []
    for file in files:
        processes.append(Popen(
            ['python3', 'Tester.py', os.path.join(folder.name, file)],
            stdout=sys.stdout if verbose else PIPE))
        time.sleep(0.1)
    passed = True
    done = False
    while not done:
        done = True
        for process in processes:
            poll = process.poll()
            if poll is None:
                done = False
            elif poll != 0:
                passed = False
    if passed:
        print(f"PASSED {folder.name}")
    else:
        print(f'one or more processes errored when running {folder.name}')
        print(f"FAILED {folder.name}")
        SUCCESS = False
    print("---------------\n")


for f in filter(lambda f: f.is_dir(), os.scandir('./tests')):
    run_test(f, verbose=False)

if SUCCESS:
    print("PASSED ALL TESTS")
    sys.exit(0)
else:
    print("DID NOT PASS ALL TESTS")
    sys.exit(-1)
