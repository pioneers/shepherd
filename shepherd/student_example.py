#pylint: disable=C0301
#pylint: disable=C0103
# pylint: disable=R1705, R1710
#pylint: disable=W0105
from math import sqrt

""" This is a document to test your code, please put your functions inside of each function and you can add your own test cases"""

"""
Do not import anything!
"""

# Problem 1


def convert_time(num):
    """
    :type num: number representing military time
    :type output list of two values representing the military time in standard time
    """
    return


# Problem 2
def eta(pos):
    """
    :type num: list representing your position as a coordinate
    :type output: the time, rounded down, it takes to travel from (5,14) to the given coordinate assuming you travel at a rate of 3 units per minute
    """
    return int(sqrt((pos[0]-5)**2+(pos[1]-14)**2) / 3)


# Problem 3
def wacky_numbers(num):
    """
    :type num: a positive integer
    :type output: an integer
    """
    return


# Problem 4
def num_increases(num):
    """
    :type num: a positive integer
    "type output: a positive integer that is the number of times the right number is greater than the left number in the input
    :RESTRICTION: YOU CANNOT TURN THE NUMBERS INTO STRINGS
    """
    return


# Problem 5
def wheresArmadillo(animals):
    """
    :type animal: list containing the names of the animals presorted by weight
    :output: the product of the number of passes through the list and the index of the armadillo
    :HINT: USE THE checkAnimal FUNCTION TO SEE IF THE ARMADILLO IS HEAVIER OR LIGHTER THAN THE GIVEN FUNCTION
    """
    return


def checkAnimal(animal):
    """
    DO NOT TOUCH THIS FUNCTION
    :type animal: String representing the name of the animal
    :output: a 1 if the armadillo is heavier than the input animal,
             a -1 if the armadillo is lighter than the input animal,
             a 0 if the armadillo is the input animal.
    """
    weights = {"mouse": 0.01, "frog": 0.1, "dove": 1, "chicken": 3, "cat": 5, "koala": 10, "dog": 15, "turkey": 20, "armadillo": 27, "alligator": 50,
               "leopard": 100, "wolf": 150, "pig": 200, "deer": 250, "lion": 300, "cow": 310, "buffalo": 400, "elephant": 500, "dinosaur": 1000}
    animalWeight = weights.get(animal)
    armadilloWeight = weights.get("armadillo")
    if animalWeight > armadilloWeight:
        return -1
    elif animalWeight < armadilloWeight:
        return 1
    elif animalWeight == armadilloWeight:
        return 0


# Problem 6
def pie_cals_triangle(num):
    """
    :type num: positive integer representing the starting number of your triangle
    :output: the sum of the first five rows of the triangle shown in the coding challenges
    """
    return


# Problem 7
def road_trip(num):
    """
    :type num: positive integer re
    :type output: integer representing the time traveled rounded to the nearest time if everytime the distance left is a multiple of five you add three units of distance, otherwise subtract two units of distance.
    :RESTRICTION YOU MUST USE RECURSION
    """
    return


# Problem 8
def convertRoman(num):
    """
    :type num: a positive integer
    :type output: the roman numeral representation of the input num
    """
    return

# Bonus Problem


def picky_rat(words):
    """
    :type words: a list of Strings
    :type output: a list of sorted strings with for string i, the ith character removed. This wraps around if i is larger than the length of the string.
    """
    return []
