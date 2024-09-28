import random

NUM_OF_LIGHTS = 5
rd = random.Random()
rd.seed(16383)
lights = [False for _ in range(NUM_OF_LIGHTS)]


def wrapper(s: str):
    match s:
        case 'a':
            return str(0)
        case 's':
            return str(1)
        case 'd':
            return str(2)
        case 'f':
            return str(3)
        case 'g':
            return str(4)
        case _:
            return s

def keyboard_input():
    line = wrapper(input())
    if line in [str(n) for n in range(NUM_OF_LIGHTS)]:
        return whack(int(line))

def whack(n: int):
    if not lights[n]:
        print("oops...")
        return False
    lights[n] = False
    return True

def print_board():
    print(''.join(["          " + ("@" if lights[n] else "-") for n in range(NUM_OF_LIGHTS)]))

def moles():
    lights[rd.randint(0, NUM_OF_LIGHTS-1)] = True

def whack_a_mole():
    print("Welcome to Whack A Mole Lite! \nLet's start a game!\n\n")
    _continue = True
    while _continue:
        moles()
        print_board()
        _continue = keyboard_input()
    print("End of game. Thanks for playing!")


whack_a_mole()
