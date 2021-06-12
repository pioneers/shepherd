import subprocess
import doctest
import os
from utils import *
import importlib
import re

# TODO: replace with this year's challenges

CH = None


def convert_time(num):
    """
    >>> convert_time(0) # same as autograder (0)
    [12, 0]
    >>> convert_time(2) # one digit number (_)
    [12, 2]
    >>> convert_time(49) # random two digit number (_._)
    [12, 49]
    >>> convert_time(30) # two digit number ending in 0 (_0)
    [12, 30]
    >>> convert_time(600) # three digit number ending in two 0’s (_00)
    [6, 0]
    >>> convert_time(309) # (_0_)
    [3, 9]
    >>> convert_time(219) # random three digit number (_._._)
    [2, 19]
    >>> convert_time(1249) # (12..)
    [12, 49]
    >>> convert_time(1341) # random four digit number
    [1, 41]
    >>> convert_time(2310) # 23..
    [11, 10]
    """
    return CH.convert_time(num)


def eta(pos):
    """
    >>> eta([5, 14]) # original position, same as autograder
    0
    >>> eta([-4, -2]) # negative coordinates
    6
    >>> eta([7, 18]) # greater than 5 and 14
    1
    >>> eta([4, 12]) # less than 5 and 14
    0
    >>> eta([4, 19]) # one less and one greater
    1
    """
    return CH.eta(pos)


def wacky_numbers(num):
    """
    >>> wacky_numbers(10) # random positive even number
    1249
    >>> wacky_numbers(-5) # random negative odd number
    -32
    >>> wacky_numbers(23) # random positive odd number
    2297
    >>> wacky_numbers(-6) # random negative even number
    -12
    >>> wacky_numbers(0) # 0
    0
    """
    return CH.wacky_numbers(num)


def num_increases(num):
    """
    >>> num_increases(1) # not large enough to qualify
    0
    >>> num_increases(127) # basic test case of increasing sequence
    2
    >>> num_increases(98431) # basic test case of decreasing sequence
    0
    >>> num_increases(149325) # test a somewhat random sequence
    3
    >>> num_increases(111111111) # flat test case
    0
    """
    return CH.num_increases(num)


def wheresArmadillo(animals):
    """
    >>> wheresArmadillo(["mouse", "frog", "chicken", "cat", "dog", "armadillo", "pig", "cow", "dinosaur"])
    15
    >>> wheresArmadillo(["mouse", "frog", "chicken", "turkey", "cat", "dog", "armadillo", "pig", "cow", "buffalo", "dinosaur"])
    24
    >>> wheresArmadillo(["mouse", "frog", "chicken", "cat", "armadillo", "alligator", "pig", "cow", "dinosaur"])
    4
    >>> wheresArmadillo(["dog", "armadillo", "pig", "cow", "buffalo", "dinosaur"])
    2
    >>> wheresArmadillo(["dog", "armadillo"])
    2
    """
    return CH.wheresArmadillo(animals)


def pie_cals_triangle(num):
    """
    >>> pie_cals_triangle(1) # small test
    15
    >>> pie_cals_triangle(100) # large test
    1000202010900
    >>> pie_cals_triangle(-1) # negative test
    -7
    >>> pie_cals_triangle(0) # zero case
    0
    """
    return CH.pie_cals_triangle(num)


def road_trip(d):
    """
    >>> road_trip(0) # zero case
    0
    >>> road_trip(12) # small test
    11
    >>> road_trip(51) # medium test
    48
    >>> road_trip(104) # large test
    102
    """
    return CH.road_trip(d)


def convertRoman(num):
    """
    >>> convertRoman(2) # number less than 4
    'II'
    >>> convertRoman(31) # two digit number without edge case
    'XXXI'
    >>> convertRoman(45) # two digit number edge case
    'XLV'
    >>> convertRoman(832) # three digit number
    'DCCCXXXII'
    >>> convertRoman(1952) # four digit number
    'MCMLII'
    """
    return CH.convertRoman(num)


def picky_rat(words):
    """
    >>> ['']
    ['']
    >>> picky_rat(['apple', 'banana', 'carrot'])
    ['pple', 'bnana', 'carot']
    >>> picky_rat(['carrot', 'banana', 'apple'])
    ['pple', 'bnana', 'carot']
    >>> picky_rat(['notarealword', 'notarealwordtoo', 'notarealwordalso'])
    ['otarealword', 'ntarealwordalso', 'noarealwordtoo']
    >>> picky_rat(['apple', 'apple', 'apple', 'apple', 'apple', 'apple'])
    ['pple', 'aple', 'aple', 'appe', 'appl', 'pple']
    >>> picky_rat(['notarealword', 'notarealwordtoo', 'notarealwordalso'])
    ['otarealword', 'ntarealwordalso', 'noarealwordtoo']
    >>> picky_rat(['a', 'e', 'i', 'o' , 'u'])
    ['', '', '', '', '']
    """
    return CH.picky_rat(words)


def get_results(ip):
    global CH
    return [True] * 8
    get_challenges(ip)
    # TODO: need feedback if they passed visible/hidden tests, also how do we tell them what they failed?

    os.system('clear')
    CH = importlib.import_module("student")
    doc_tests = doctest.DocTestFinder()

    easy_challenges = [eta, convert_time]
    hard_challenges = [picky_rat, convertRoman]

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
