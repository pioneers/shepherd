import random, threading, time, queue
from ydl import Client
from utils import *

NUM_OF_LIGHTS = 3
rd = random.Random()
rd.seed(16383)
lights = [False for _ in range(NUM_OF_LIGHTS)]
q = queue.Queue()
yc = Client(YDL_TARGETS.SHEPHERD)


def wrapper(s: str):
    match s:
        case 'a':
            return str(0)
        case 's':
            return str(1)
        case 'd':
            return str(2)
        case _:
            return s

def keyboard_input():
    while True:
        line = wrapper(input())
        if line in [str(n) for n in range(NUM_OF_LIGHTS)]:
            whack(int(line))
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=int(line)))


def whack(n: int):
    q.put(n)


def turn_on(n: int):
    lights[n] = True
    yc.send(SHEPHERD_HEADER.TURN_ON_BUTTON_LIGHT(n))
    
def turn_off(n: int):
    lights[n] = False
    yc.send(SHEPHERD_HEADER.TURN_OFF_BUTTON_LIGHT(n))


def moles():
    turn_on(rd.randint(0, NUM_OF_LIGHTS-1))

def whack_a_mole():
    print("Welcome to Whack A Mole! \nLet's start a game!\n\n")
    time.sleep(.5)
    interval = .75
    correct = True
    try:
        while correct:
            moles()
            while not q.empty(): q.get()        # clear the queue, avoid vibro-tapping
            waited = 0
            correct = False
            while not q.empty() or waited < interval:
                waited += 0.01
                time.sleep(0.01)
                try:
                    n = q.get(False)
                except queue.Empty:
                    continue
                if not lights[n]:
                    turn_on(n)
                    print("oops...")
                    # correct = False
                    raise StopIteration
                else:
                    turn_off(n)
                    print("GOOD!")
                    time.sleep(.2)
                    correct = True
                    break
            if not correct:
                raise StopIteration
    except StopIteration:
        [turn_off(n) if lights[n] else None for n in range(NUM_OF_LIGHTS)]
        turn_off(0)
        turn_off(0)
        time.sleep(1)
    print("\nEnd of game. Thanks for playing!")


threading.Thread(target=keyboard_input, args=(), daemon=True).start()
whack_a_mole()
