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


def turn_all_lights(alliance, on):
    head = SENSOR_HEADER.TURN_ON_BUTTON_LIGHT if on else SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT
    if alliance == ALLIANCE_COLOR.BLUE:
        ar = [0, 1, 2, 3, 4, 5]
    else:
        ar = [6, 7, 8, 9, 10, 11]
    for i in ar:
        YC.send((YDL_TARGETS.SENSORS, head.name, {"id": i}))


def cheat_codes(alliance_lst, code):
    if alliance_lst == 'BLUE_CHEAT_CODE':
        CHEAT_CODE = [hash(c) % NUM_BUTTONS for c in code]
    else:  # alliance == 'GOLD_CHEAT_CODE'
        CHEAT_CODE = [hash(c) % NUM_BUTTONS + NUM_BUTTONS for c in code]
    return CHEAT_CODE


def send_security_breach_score(alliance, done):
    YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_SECURITY_BREACH_SCORE,
             {"alliance": alliance, "done": done}))


def send_cheat_code_score(alliance, CHEAT_CODE_DONE):
    YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_CHEAT_CODE_SCORE,
             {"alliance": alliance, "score": CHEAT_CODE_DONE}))

# for both of the cheat code


def set_cheat_code(alliance, CHEAT_CODE):
    YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.SET_CHEAT_CODE,
             {"alliance": alliance, "CHEAT_CODE": CHEAT_CODE}))

# check live coding status


def check_live_coding(alliance):
    return True


def fill_queue():
    while True:
        msg = YC.receive()
        print(msg)
        if msg[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
            if msg[2]['id'] < NUM_BUTTONS:
                BLUE_QUEUE.put(msg)  # coming from sensors when being paused
            else:
                GOLD_QUEUE.put(msg)

        if msg[1] in [SHEPHERD_HEADER.START_NEXT_STAGE.name, SHEPHERD_HEADER.SETUP_MATCH.name]:
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
        "BULE_CHEAT_CODE" if alliance == ALLIANCE_COLOR.BLUE else "GOLD_CHEAT_CODE", REQUIREMENT)

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
        YC.send(
            (YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {"id": button}))

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

            if message[1] in [SHEPHERD_HEADER.START_NEXT_STAGE.name, SHEPHERD_HEADER.SETUP_MATCH.name]:
                turn_all_lights(alliance, on=False)
                streak = 0
                max_streak = 0
                cheat_code_press_count = 0
                CHEAT_CODE = make_cheat_code(
                    "BULE_CHEAT_CODE" if alliance == ALLIANCE_COLOR.BLUE else "GOLD_CHEAT_CODE", REQUIREMENT)
                set_cheat_code(alliance, CHEAT_CODE)

            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
                # print("III pressed: " + str(message[2]["id"]))
                PRESSED_ID = int(message[2]["id"])
                YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {
                        "id": PRESSED_ID}))
                time.sleep(0.2)
                YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {
                        "id": PRESSED_ID}))
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
        YC.send((YDL_TARGETS.SENSORS,
                SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {"id": button}))
        """
        if (not pressed):
            # print("not pressed")
            YC.send((YDL_TARGETS.UI, UI_HEADER.GAME_OVER.name, { }))
        
            return
        
        sleeptime = random.random() + 1
        time.sleep(sleeptime)
        """

# threading.Thread(target=fill_queue, args=(), daemon=True).start()
# start_helper()

# EVERYWHERE_FUNCTIONS = {
#     SHEPHERD_HEADER.START_WHACKAMOLE.name: start_whackamole,
# }


threading.Thread(target=whack_a_mole_start, args=(
    ALLIANCE_COLOR.BLUE,), daemon=True).start()
threading.Thread(target=whack_a_mole_start, args=(
    ALLIANCE_COLOR.GOLD,), daemon=True).start()
fill_queue()
