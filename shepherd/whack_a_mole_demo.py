import time
import random
import queue
import threading
from ydl import Client
import copy
from utils import *


"""
Make sure to update the number of buttons used
"""
NUM_BUTTONS = 3
YC = Client(YDL_TARGETS.SHEPHERD)
EVENT_QUEUE = queue.Queue()


def turn_on_light(id):
    print("light up", id)
    YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(id))


def turn_off_light(id):
    print("turn off", id)
    YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(id))


def turn_all_lights(on):
    for i in range(NUM_BUTTONS):
        turn_on_light(i) if on else turn_off_light(i)


"""
Stores all of the YDL calls in EVENT_QUEUE
"""
def fill_queue():
    while True:
        msg = YC.receive()
        print(msg)
        if msg[1] == 'button_press':
            EVENT_QUEUE.put(msg)

        if msg[1] in ["start_next_stage", "setup_match"]:   # Impossible to reach if running whack-a-mole demo
            EVENT_QUEUE.put(msg)



### NEW CODE (2024 Ver.) FOR ACTUAL GAME PURPOSE ###

# def whack_a_mole_start(alliance):

#     turn_all_lights(alliance, on=False)

#     mole_press_count = 0
#     CHEAT_CODE_DONE = 0
#     MOLE_PRESS_DONE = False
#     EVENT_QUEUE = BLUE_QUEUE if alliance == ALLIANCE_COLOR.BLUE else GOLD_QUEUE
#     CHEAT_CODE = make_cheat_code(alliance)
#     CHEAT_CODE_1, CHEAT_CODE_2 = CHEAT_CODE[:5], CHEAT_CODE[5:]
#     CHEAT_CODE_COPY_1, CHEAT_CODE_COPY_2 = copy.deepcopy(CHEAT_CODE_1), copy.deepcopy(CHEAT_CODE_2)

#     """
#         When the function starts
#         1. Button chosen
#         2. Clear the ydl calls
#         3. Button light turns on
#         4. Enter the while loop
#         DELAY: the time we have to pause the button
#         waited: time passed
#         """
#     while True:
#         # print("start score: " + str(score))
#         if alliance == ALLIANCE_COLOR.BLUE:
#             button = int(random.random() * NUM_BUTTONS)
#         else:
#             button = int(random.random() * NUM_BUTTONS) + NUM_BUTTONS
#         turn_on_light(button)

#         while not EVENT_QUEUE.empty():
#             # clear the queue (The remaining ydl calls received)
#             EVENT_QUEUE.get(True)

#         waited = 0
#         correct_pressed = False
#         cheat_code_pressed = False

#         # while received a ydl call or we still have time
#         while (not EVENT_QUEUE.empty()) or (waited < DELAY) and not (correct_pressed or cheat_code_pressed):
#             waited += 0.01
#             time.sleep(0.01)
#             try:
#                 message = EVENT_QUEUE.get(False)
#             except queue.Empty:
#                 continue  # go back to the top of the while loop

#             if message[1] in ["start_next_stage", "setup_match"]:
#                 turn_all_lights(alliance, on=False)
#                 CHEAT_CODE_DONE = 0
#                 mole_press_count = 0
#                 MOLE_PRESS_DONE = False
#                 CHEAT_CODE = make_cheat_code(alliance)
#                 CHEAT_CODE_1, CHEAT_CODE_2 = CHEAT_CODE[:5], CHEAT_CODE[5:]
#                 CHEAT_CODE_COPY_1, CHEAT_CODE_COPY_2 = copy.deepcopy(CHEAT_CODE_1), copy.deepcopy(CHEAT_CODE_2)

#             if message[1] == 'button_press':
#                 PRESSED_ID = int(message[2]['id'])
#                 print("Button pressed:", PRESSED_ID)
#                 turn_on_light(PRESSED_ID)
#                 time.sleep(0.2)
#                 turn_off_light(PRESSED_ID)

#                 if PRESSED_ID == button:
#                     correct_pressed = True

#                 if check_live_coding(alliance):
#                     if len(CHEAT_CODE_1) > 0 or len(CHEAT_CODE_2) > 0:
#                         if PRESSED_ID == CHEAT_CODE_1[0]:
#                             print("Cheat code 1 pop: ", CHEAT_CODE_1[0])
#                             CHEAT_CODE_1.pop(0)
#                             print("Cheat code 1: ", CHEAT_CODE)
#                             cheat_code_pressed = (len(CHEAT_CODE_1) == 0)
#                         else:
#                             print("Reset cheat_code 1")
#                             # reset cheat_code, if cheat code is not done in order
#                             CHEAT_CODE_1 = CHEAT_CODE_COPY_1
#                             CHEAT_CODE_COPY_1 = copy.deepcopy(CHEAT_CODE_COPY_1)
#                             print(CHEAT_CODE_1)

                            
#                         if PRESSED_ID == CHEAT_CODE_2[0]:
#                             print("Cheat code pop 2: ", CHEAT_CODE_2[0])
#                             CHEAT_CODE_2.pop(0)
#                             print("Cheat code 2: ", CHEAT_CODE)
#                             cheat_code_pressed = (len(CHEAT_CODE_2) == 0)
#                         else:
#                             print("Reset cheat_code 2")
#                             # reset cheat_code, if cheat code is not done in order
#                             CHEAT_CODE_2 = CHEAT_CODE_COPY_2
#                             CHEAT_CODE_COPY_2 = copy.deepcopy(CHEAT_CODE_COPY_2)
#                             print(CHEAT_CODE_2)

#         if correct_pressed:
#             mole_press_count += 1
#             # print(f"got {button} in {round(waited,2)} seconds", end=" ")
#             print(f"Correct presses: {mole_press_count}")
#             turn_all_lights(alliance, on=True)
#             time.sleep(0.2)
#             turn_all_lights(alliance, on=False)

#         if cheat_code_pressed:
#             CHEAT_CODE_DONE += 1
#             cheat_code_pressed = False
#             send_cheat_code_score(alliance, CHEAT_CODE_DONE)
#             celebrate(alliance)

#         if mole_press_count == REQUIREMENT:
#             mole_press_count += 1
#             MOLE_PRESS_DONE = True
#             celebrate(alliance)
#             send_security_breach_score(alliance, MOLE_PRESS_DONE)

#         turn_off_light(button)
#         send_cheat_code_score(alliance, CHEAT_CODE_DONE)
#         send_security_breach_score(alliance, MOLE_PRESS_DONE)


# threading.Thread(target=whack_a_mole_start, args=(
#     ALLIANCE_COLOR.BLUE,), daemon=True).start()
# threading.Thread(target=whack_a_mole_start, args=(
#     ALLIANCE_COLOR.GOLD,), daemon=True).start()
# fill_queue()


"""
Reads all of the YDL calls stored in EVENT_QUEUE. 
Only accept the YDL call if the YDL call wants to 
run the function START_WHACKAMOLE (which is start())
"""
def start_helper():
    # start()
    while True:
        if (not EVENT_QUEUE.empty()):
            try:
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue
            if message[1] == SHEPHERD_HEADER.START_WHACKAMOLE.name:
                start()

def start():
    # ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT.name, {"id": 1})
    # print("banana boat")

    # while True:
    #     turn_all_lights(on=False)
    #     time.sleep(1)
    #     turn_all_lights(on=True)
    #     time.sleep(1)
    
    turn_all_lights(on=False)
    score = 0
    YC.send((YDL_TARGETS.UI, UI_HEADER.UPDATE_PLAYER_SCORE.name, {"score": score}))
    while True:
        # print("start score: " + str(score))
        button = int(random.random()*NUM_BUTTONS)
        YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {"id": button}))
        
        while not EVENT_QUEUE.empty(): EVENT_QUEUE.get(True) # clear the queue 
        delay = random.random()
        delay = delay if delay > .4 else .4
        delay *= 2
        waited = 0
        pressed = False
        while (not EVENT_QUEUE.empty()) or (waited < delay and not pressed):
            waited += 0.01
            time.sleep(0.01)
            try:
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue  
            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
                # print("III pressed: " + str(message[2]["id"]))
                if int(message[2]["id"]) == button:
                    pressed = True
        if pressed:
            print(f"got {button} in {round(waited,2)} seconds", end=" ")
            score += 1
            turn_all_lights(on=True)
            time.sleep(0.1)
            turn_all_lights(on=False)
        else:
            print(f":( {button}", end=" ")
        print(f'score: {score}')
        YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {"id": button}))
        YC.send((YDL_TARGETS.UI, UI_HEADER.UPDATE_PLAYER_SCORE.name, {"score": score}))
        if (not pressed):
            # print("not pressed")
            YC.send((YDL_TARGETS.UI, UI_HEADER.GAME_OVER.name, { }))
            return
        # sleeptime = random.random() + 1
        time.sleep(0.1)

threading.Thread(target=fill_queue, args=(), daemon=True).start()
start_helper()
