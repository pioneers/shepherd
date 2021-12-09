import subprocess
import doctest
import os
from utils import *
import importlib
import re

# student module
CH = None

# example problem
def add_two_numbers(num1, num2):
    """
    >>> add_two_numbers(0,0)
    0
    >>> add_two_numbers(2,-3)
    -1
    >>> add_two_numbers(30,10)
    40
    """
    return CH.add_two_numbers(num1, num2)


def get_results(ip):
    global CH
    return [True] * 8
    get_challenges(ip)
    # TODO: need feedback if they passed visible/hidden tests, also how do we tell them what they failed?

    os.system('clear')
    CH = importlib.import_module("student")
    doc_tests = doctest.DocTestFinder()

    easy_challenges = [add_two_numbers]
    hard_challenges = []

    easy_passed = run_set_of_tests(doc_tests, easy_challenges)
    hard_passed = run_set_of_tests(doc_tests, hard_challenges)
    print(easy_passed)
    print(hard_passed)

    

    # TODO: get the challenge results as list of bools ([passed challenge 1, passed challenge 2, etc.])

    #                              list of:
    # +------+                   +---------+
    # |module| --DocTestFinder-> | DocTest | --DocTestRunner-> results
    # +------+    |        ^     +---------+     |       ^    (printed)
    #             |        |     | Example |     |       |
    #             v        |     |   ...   |     v       |
    #            DocTestParser   | Example |   OutputChecker
    #                            +---------+


def get_challenges(ip):
    subprocess.call(['./student_code.sh', ip])


def run_set_of_tests(doc_test, test_set):
    """
    takes a list of functions, returns True if all doctests pass.
    """
    passed = True
    for test in test_set:
        passed = passed and run_autograder_on_function(doc_test, test) == 0
    return passed


def run_autograder_on_function(doc_tests, function):
    failed = 0
    for doc_test in doc_tests.find(function):
        failed += doctest.DocTestRunner().run(doc_test)[0]
    return failed
