import time
import random
import queue
import threading
from ydl import Client
import copy
from utils import *


REQUIREMENT = 5
NUM_BUTTONS = 6
YC = Client(YDL_TARGETS.SHEPHERD)
BLUE_QUEUE = queue.Queue()
GOLD_QUEUE = queue.Queue()
DELAY = 30


def turn_on_light(id):
    print("light up", id)
    YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id))


def turn_off_light(id):
    print("turn off", id)
    YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id))


def turn_all_lights(alliance, on):
    ar = [0, 1, 2, 3, 4, 5] if alliance == ALLIANCE_COLOR.BLUE else [
        6, 7, 8, 9, 10, 11]
    for i in ar:
        turn_on_light(i) if on else turn_off_light(i)


def send_security_breach_score(alliance, done):
    YC.send((SHEPHERD_HEADER.UPDATE_SECURITY_BREACH_SCORE(alliance, done)))


def send_cheat_code_score(alliance, CHEAT_CODE_DONE):
    YC.send((SHEPHERD_HEADER.UPDATE_CHEAT_CODE_SCORE(alliance, CHEAT_CODE_DONE)))


def set_cheat_code(alliance, CHEAT_CODE):
    YC.send((SHEPHERD_HEADER.SET_CHEAT_CODE(alliance, CHEAT_CODE)))


def check_live_coding(alliance):
    return True


def fill_queue():
    while True:
        msg = YC.receive()
        print(msg)
        if msg[1] == 'button_press':
            if msg[2]['id'] < NUM_BUTTONS:
                BLUE_QUEUE.put(msg)  # coming from sensors when being paused
            else:
                GOLD_QUEUE.put(msg)

        if msg[1] in ["start_next_stage", "setup_match"]:
            BLUE_QUEUE.put(msg)
            GOLD_QUEUE.put(msg)
#


def make_cheat_code(alliance):
    CHEAT_CODE = [random.randint(0, 5) for _ in range(10)]
    set_cheat_code(alliance, CHEAT_CODE)
    if alliance == ALLIANCE_COLOR.GOLD:
        CHEAT_CODE = [i + 5 for i in CHEAT_CODE]
    return CHEAT_CODE


def celebrate(alliance):
    print("CHEAT CODE BONUS!!!")
    turn_all_lights(alliance, on=True)
    time.sleep(0.1)
    turn_all_lights(alliance, on=False)
    time.sleep(0.1)
    turn_all_lights(alliance, on=True)
    time.sleep(0.1)
    turn_all_lights(alliance, on=False)
    time.sleep(0.1)
    turn_all_lights(alliance, on=True)
    time.sleep(0.1)
    turn_all_lights(alliance, on=False)
    time.sleep(0.1)
    turn_all_lights(alliance, on=True)
    time.sleep(0.1)
    turn_all_lights(alliance, on=False)
    time.sleep(0.1)
    turn_all_lights(alliance, on=True)
    time.sleep(0.1)
    turn_all_lights(alliance, on=False)
    return True


def whack_a_mole_start(alliance):

    turn_all_lights(alliance, on=False)

    mole_press_count = 0
    CHEAT_CODE_DONE = 0
    MOLE_PRESS_DONE = False
    EVENT_QUEUE = BLUE_QUEUE if alliance == ALLIANCE_COLOR.BLUE else GOLD_QUEUE
    CHEAT_CODE = make_cheat_code(alliance)
    CHEAT_CODE_COPY = copy.deepcopy(CHEAT_CODE)

    """
        When the function starts
        1. Button chosen
        2. Clear the ydl calls
        3. Button light turns on
        4. Enter the while loop
        DELAY: the time we have to pause the button
        waited: time passed
        """
    while True:
        # print("start score: " + str(score))
        if alliance == ALLIANCE_COLOR.BLUE:
            button = int(random.random() * NUM_BUTTONS)
        else:
            button = int(random.random() * NUM_BUTTONS) + NUM_BUTTONS
        turn_on_light(button)

        while not EVENT_QUEUE.empty():
            # clear the queue (The remaining ydl calls received)
            EVENT_QUEUE.get(True)

        waited = 0
        correct_pressed = False
        cheat_code_pressed = False

        # while received a ydl call or we still have time
        while (not EVENT_QUEUE.empty()) or (waited < DELAY) and not (correct_pressed or cheat_code_pressed):
            waited += 0.01
            time.sleep(0.01)
            try:
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue  # go back to the top of the while loop

            if message[1] in ["start_next_stage", "setup_match"]:
                turn_all_lights(alliance, on=False)
                CHEAT_CODE_DONE = 0
                mole_press_count = 0
                MOLE_PRESS_DONE = False
                CHEAT_CODE = make_cheat_code(alliance)
                CHEAT_CODE_COPY = copy.deepcopy(CHEAT_CODE)

            if message[1] == 'button_press':
                PRESSED_ID = int(message[2]['id'])
                print("Button pressed:", PRESSED_ID)
                turn_on_light(PRESSED_ID)
                time.sleep(0.2)
                turn_off_light(PRESSED_ID)

                if PRESSED_ID == button:
                    correct_pressed = True

                if check_live_coding(alliance):
                    if len(CHEAT_CODE) > 0:
                        if PRESSED_ID == CHEAT_CODE[0]:
                            print("Cheat code pop: ", CHEAT_CODE[0])
                            CHEAT_CODE.pop(0)
                            print("Cheat code: ", CHEAT_CODE)
                            cheat_code_pressed = len(
                                CHEAT_CODE) == 5 or len(CHEAT_CODE) == 0
                        else:
                            print("Reset cheat_code")
                            # reset cheat_code, if cheat code is not done in order
                            CHEAT_CODE = CHEAT_CODE_COPY[-5:] if len(
                                CHEAT_CODE) <= 5 else CHEAT_CODE_COPY
                            CHEAT_CODE_COPY = copy.deepcopy(CHEAT_CODE_COPY)
                            print(CHEAT_CODE)

        if correct_pressed:
            mole_press_count += 1
            # print(f"got {button} in {round(waited,2)} seconds", end=" ")
            print(f"Correct presses: {mole_press_count}")
            turn_all_lights(alliance, on=True)
            time.sleep(0.2)
            turn_all_lights(alliance, on=False)

        if cheat_code_pressed:
            CHEAT_CODE_DONE += 1
            cheat_code_pressed = False
            send_cheat_code_score(alliance, CHEAT_CODE_DONE)
            celebrate(alliance)

        if mole_press_count == REQUIREMENT:
            mole_press_count += 1
            MOLE_PRESS_DONE = True
            celebrate(alliance)
            send_security_breach_score(alliance, MOLE_PRESS_DONE)

        turn_off_light(button)
        send_cheat_code_score(alliance, CHEAT_CODE_DONE)
        send_security_breach_score(alliance, MOLE_PRESS_DONE)


threading.Thread(target=whack_a_mole_start, args=(
    ALLIANCE_COLOR.BLUE,), daemon=True).start()
threading.Thread(target=whack_a_mole_start, args=(
    ALLIANCE_COLOR.GOLD,), daemon=True).start()
fill_queue()
