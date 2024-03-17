import time
import random
import queue
import threading
from ydl import Client
from utils import *


NUM_BUTTONS = 6
REQUIREMENT = 5
YC = Client(YDL_TARGETS.SHEPHERD)
BLUE_QUEUE = queue.Queue()
GOLD_QUEUE = queue.Queue()




def turn_all_lights(alliance, on):
    head = SENSOR_HEADER.TURN_ON_BUTTON_LIGHT if on else SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT
    if alliance == ALLIANCE_COLOR.BLUE:
        ar = [0, 1, 2, 3, 4, 5]
    else:
        ar = [6, 7, 8, 9, 10, 11]
    for i in ar:
        YC.send((YDL_TARGETS.SENSORS, head.name, {"id": i}))


def cheat_codes(alliance, code):
    if alliance == 'blue':
        CHEAT_CODE = [hash(c) % NUM_BUTTONS for c in code] #change this!! cheat code button id order
    else: #alliance == 'gold'
        CHEAT_CODE = [hash(c) % NUM_BUTTONS + NUM_BUTTONS for c in code] #change this!! cheat code button id order
    return CHEAT_CODE


# def send_score(alliance, max_streak, cheat_code_done):
#     score = 0
#     if max_streak in [1, 2]:
#         score = 20
#     if max_streak in [3, 4]:
#         score = 40
#     if max_streak in [5, 6]:
#         score = 60
#     if max_streak >= 7:
#         score = 80
#         # return # do we actually want to end the game if streak 7? 
#     
#     if cheat_code_done:
#         score += 100
#         
#     YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_WHACK_A_MOLE_SCORE.name, {"alliance": alliance, "score": score})) 
#     print(f'score: {score}')
#     print(f'alliance: {alliance}')

def send_score(alliance, num_whack_pressed, num_cheat_pressed):
    YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_WHACK_A_MOLE_SCORE.name, \
             {"alliance": alliance, "outcome": (num_whack_pressed >= REQUIREMENT, num_cheat_pressed >= REQUIREMENT)}))


def fill_queue():
    while True:
        msg = YC.receive()
        print(msg)
        if msg[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
            if msg[2]['id'] < NUM_BUTTONS:
                BLUE_QUEUE.put(msg) #coming from sensors when being paused
            else:
                GOLD_QUEUE.put(msg)

        if msg[1] in [SHEPHERD_HEADER.START_NEXT_STAGE.name, SHEPHERD_HEADER.SETUP_MATCH.name]:
            BLUE_QUEUE.put(msg)
            GOLD_QUEUE.put(msg)


# def start_whackamole():
#     start()

# def start_helper():
#     # start()
#     while True:
#         if (not EVENT_QUEUE.empty()):
#             try:
#                 message = EVENT_QUEUE.get(False)
#             except queue.Empty:
#                 continue
#             if message[1] == SHEPHERD_HEADER.START_WHACKAMOLE.name:
#                 whack_a_mole_start()

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
    streak = 0
    max_streak = 0
    cheat_code_done = False
    send_score(alliance, max_streak, cheat_code_done)
    CHEAT_CODE, REVERSED_CHEAT_CODE = cheat_codes(alliance)
    EVENT_QUEUE = BLUE_QUEUE if alliance == ALLIANCE_COLOR.BLUE else GOLD_QUEUE

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
            button = int(random.random()*NUM_BUTTONS)
        else:
            button = int(random.random()*NUM_BUTTONS) + NUM_BUTTONS
        YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {"id": button}))
        
        while not EVENT_QUEUE.empty(): EVENT_QUEUE.get(True) # clear the queue (The remaining ydl calls received)
        delay = 30
        waited = 0
        pressed = False
        cheat_code_pressed = False


        # while received a ydl call or we still have time
        while (not EVENT_QUEUE.empty()) or (waited < delay and not (pressed or cheat_code_pressed)):
            waited += 0.01            
            time.sleep(0.01)
            try:                
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue #go back to the top of the while loop

            if message[1] in [SHEPHERD_HEADER.START_NEXT_STAGE.name, SHEPHERD_HEADER.SETUP_MATCH.name]:
                turn_all_lights(alliance, on=False)
                streak = 0
                max_streak = 0
                cheat_code_done = False
                CHEAT_CODE, REVERSED_CHEAT_CODE = cheat_codes(alliance)


            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
                # print("III pressed: " + str(message[2]["id"]))
                PRESSED_ID = int(message[2]["id"])
                YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {"id": PRESSED_ID}))
                time.sleep(0.2)
                YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {"id": PRESSED_ID}))
                if PRESSED_ID == button:
                    pressed = True
                else:
                    streak = 0
                    print(f"streak: {streak}, max_streak: {max_streak}")
                
                print("cheat code", CHEAT_CODE, end="")
                if PRESSED_ID == CHEAT_CODE[-1]:                    
                    CHEAT_CODE.pop()
                else:
                    CHEAT_CODE, REVERSED_CHEAT_CODE = cheat_codes(alliance)
                print("after", CHEAT_CODE)
                
                cheat_code_pressed = len(CHEAT_CODE) == 0 or len(REVERSED_CHEAT_CODE) == 0
                if cheat_code_pressed:
                    cheat_code_done = True
                    CHEAT_CODE, REVERSED_CHEAT_CODE = cheat_codes(alliance)



        if pressed:
            #print(f"got {button} in {round(waited,2)} seconds", end=" ")
            streak += 1
            max_streak = max(max_streak, streak)
            print(f"streak: {streak}, max_streak: {max_streak}")
            turn_all_lights(alliance, on=True)
            time.sleep(0.2)
            turn_all_lights(alliance, on=False)


        if cheat_code_pressed:
            print("CHEAT CODE bonus")
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
            # return # do we actually want to end the game 
        
        send_score(alliance, max_streak, cheat_code_done)
        YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {"id": button}))
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

threading.Thread(target=whack_a_mole_start, args=(ALLIANCE_COLOR.BLUE,), daemon=True).start()
threading.Thread(target=whack_a_mole_start, args=(ALLIANCE_COLOR.GOLD,), daemon=True).start()
fill_queue()
