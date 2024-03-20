import time
import random
import queue
import threading
from ydl import Client
from utils import *

NUM_BUTTONS = 6
YC = Client(YDL_TARGETS.SHEPHERD)
BLUE_QUEUE = queue.Queue()
GOLD_QUEUE = queue.Queue()
BLUE_CHEAT_CODE = [[], []]
GOLD_CHEAT_CODE = [[], []]


def turn_on_light(id):
    YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id))


def turn_off_light(id):
    YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id))


def turn_all_lights(alliance, on):
    ar = [0, 1, 2, 3, 4] if alliance == ALLIANCE_COLOR.BLUE else [5, 6, 7, 8, 9]
    for i in ar:
        turn_on_light(i) if on else turn_off_light(i)


def cheat_codes(alliance_lst, code):
    if alliance_lst == 'BLUE_CHEAT_CODE':
        CHEAT_CODE = [hash(c) % NUM_BUTTONS for c in code]
    else:  # alliance == 'GOLD_CHEAT_CODE'
        CHEAT_CODE = [hash(c) % NUM_BUTTONS + NUM_BUTTONS for c in code]
    return CHEAT_CODE


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
        if msg[1] == SHEPHERD_HEADER.BUTTON_PRESS:
            if msg[2]['id'] < NUM_BUTTONS:
                BLUE_QUEUE.put(msg)  # coming from sensors when being paused
            else:
                GOLD_QUEUE.put(msg)

        if msg[1] in [SHEPHERD_HEADER.START_NEXT_STAGE, SHEPHERD_HEADER.SETUP_MATCH]:
            BLUE_QUEUE.put(msg)
            GOLD_QUEUE.put(msg)


# make a list of two cheat code lists for one alliance e.g. [[12335], [14352]]
def make_cheat_code(alliance, nums):
    for index in range(2):
        eval(alliance)[index] = cheat_codes(alliance, ''.join(
            [chr(random.randint(32, 126)) for _ in range(nums)]))
    return eval(alliance)


def celebrate(alliance):
    if cheat_code_pressed:
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
        cheat_code_pressed = False
        return True


def whack_a_mole_start(alliance):
    # alliance: blue or gold
    # ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT.name, {"id": 1})
    # print("banana boat")
    """
    while True:
        turn_all_lights(alliance, on=False)
        time.sleep(1)
        turn_all_lights(alliance, on=True)
        time.sleep(1)
    """

    turn_all_lights(alliance, on=False)
    REQUIREMENT = 5
    CHEAT_CODE_DONE = 0
    send_cheat_code_score(alliance, CHEAT_CODE_DONE)
    send_security_breach_score(alliance, False)
    EVENT_QUEUE = BLUE_QUEUE if alliance == ALLIANCE_COLOR.BLUE else GOLD_QUEUE
    CHEAT_CODE = make_cheat_code(
        "BLUE_CHEAT_CODE" if alliance == ALLIANCE_COLOR.BLUE else "GOLD_CHEAT_CODE", REQUIREMENT)

    """
        When the function starts
        1. Button chosen
        2. Clear the ydl calls
        3. Button light turns on
        4. Enter the while loop
        delay: the time we have to pause the button
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
        delay = 30
        waited = 0
        pressed = False
        cheat_code_completion = 0

        # while received a ydl call or we still have time
        while (not EVENT_QUEUE.empty()) or (waited < delay):
            waited += 0.01
            time.sleep(0.01)
            try:
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue  # go back to the top of the while loop

            if message[1] in [SHEPHERD_HEADER.START_NEXT_STAGE, SHEPHERD_HEADER.SETUP_MATCH]:
                turn_all_lights(alliance, on=False)
                cheat_code_press_count = 0
                CHEAT_CODE = make_cheat_code(
                    "BLUE_CHEAT_CODE" if alliance == ALLIANCE_COLOR.BLUE else "GOLD_CHEAT_CODE", REQUIREMENT)
                set_cheat_code(alliance, CHEAT_CODE)

            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS:
                # print("III pressed: " + str(message[2]["id"]))
                PRESSED_ID = int(message[2]["id"])
                turn_on_light(PRESSED_ID)
                time.sleep(0.2)
                turn_off_light(PRESSED_ID)
                if PRESSED_ID == button:
                    pressed = True
                else:
                    streak = 0
                    print(f"streak: {streak}, max_streak: {max_streak}")

                print("cheat code", CHEAT_CODE, end="")
                if cheat_code_completion != 2:
                    if cheat_code_press_count < REQUIREMENT and PRESSED_ID == CHEAT_CODE[0][0]:
                        CHEAT_CODE[0].pop(0)
                        cheat_code_press_count += 1
                    elif PRESSED_ID == CHEAT_CODE[1][0]:
                        CHEAT_CODE[1].pop(0)
                        cheat_code_press_count += 1
                print("after", CHEAT_CODE)

                cheat_code_completion = cheat_code_press_count // REQUIREMENT

        if pressed:
            # print(f"got {button} in {round(waited,2)} seconds", end=" ")
            streak += 1
            max_streak = max(max_streak, streak)
            print(f"streak: {streak}, max_streak: {max_streak}")
            turn_all_lights(alliance, on=True)
            time.sleep(0.2)
            turn_all_lights(alliance, on=False)

        if not cheat_code_press_count % REQUIREMENT:
            celebrate(alliance)
            send_security_breach_score(cheat_code_completion)
            # return
            # do we actually want to terminate this game

        send_cheat_code_score(alliance, cheat_code_press_count)
        turn_off_light(button)


threading.Thread(target=whack_a_mole_start, args=(
    ALLIANCE_COLOR.BLUE,), daemon=True).start()
threading.Thread(target=whack_a_mole_start, args=(
    ALLIANCE_COLOR.GOLD,), daemon=True).start()
fill_queue()
