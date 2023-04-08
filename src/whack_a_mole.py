import time
import random
import queue
import threading
from ydl import YDLClient
from utils import *


NUM_BUTTONS = 5
YC = YDLClient(YDL_TARGETS.SHEPHERD)
BLUE_QUEUE = queue.Queue()
GOLD_QUEUE = queue.Queue()




def turn_all_lights(alliance, on):
    head = SENSOR_HEADER.TURN_ON_BUTTON_LIGHT if on else SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT
    if alliance == ALLIANCE_COLOR.BLUE:
        ar = [0, 1, 2, 3, 4]
    else:
        ar = [5, 6, 7, 8, 9]
    for i in ar:
        YC.send((YDL_TARGETS.SENSORS, head.name, {"id": i}))


def cheat_codes(alliance):
    if alliance == 'blue':
        CHEAT_CODE = [0, 1, 2, 3, 4, 3, 2, 1, 0] #change this!! cheat code button id order
        REVERSED_CHEAT_CODE = [4-a for a in CHEAT_CODE] 
    else: #alliance == 'gold'
        CHEAT_CODE = [5, 6, 7, 8, 9, 8, 7, 6, 5] #change this!! cheat code button id order
        REVERSED_CHEAT_CODE = [14-a for a in CHEAT_CODE]
    return (CHEAT_CODE, REVERSED_CHEAT_CODE)

def fill_queue():
    while True:
        msg = YC.receive()
        print(msg)
        if msg[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
            if msg[2]['id'] < NUM_BUTTONS:
                BLUE_QUEUE.put(msg) #coming from sensors when being paused
            else:
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
    #alliance: blue or gold
    #ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT.name, {"id": 1})
    #print("banana boat")
    """
    while True:
        turn_all_lights(alliance, on=False)
        time.sleep(1)
        turn_all_lights(alliance, on=True)
        time.sleep(1)
    """


    turn_all_lights(alliance, on=False)
    score = 0
    STREAK = 0
    YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_WHACK_A_MOLE_SCORE.name, {"alliance": alliance, "score": score})) 
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
        cheat_code_done = False


        # while received a ydl call or we still have time
        while (not EVENT_QUEUE.empty()) or (waited < delay and not (pressed or cheat_code_done)):
            waited += 0.01            
            time.sleep(0.01)
            try:                
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue #go back to the top of the while loop


            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
                # print("III pressed: " + str(message[2]["id"]))
                PRESSED_ID = int(message[2]["id"])
                YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {"id": PRESSED_ID}))
                time.sleep(0.2)
                YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {"id": PRESSED_ID}))
                if PRESSED_ID == button:
                    pressed = True
                print("cheat code", CHEAT_CODE)
                if PRESSED_ID == CHEAT_CODE[-1]:
                    print("cheat code pressed", PRESSED_ID)
                    
                    CHEAT_CODE.pop()
                    print("cheat code", CHEAT_CODE)
                if PRESSED_ID == REVERSED_CHEAT_CODE[-1]:
                    print("cheat code pressed", PRESSED_ID)
                    REVERSED_CHEAT_CODE.pop()
                    print("cheat code", CHEAT_CODE)
                
                cheat_code_done = len(CHEAT_CODE) == 0 or len(REVERSED_CHEAT_CODE) == 0

        if pressed:
            #print(f"got {button} in {round(waited,2)} seconds", end=" ")
            STREAK += 1
            print("STREAK" , STREAK)
            turn_all_lights(alliance, on=True)
            time.sleep(0.2)
            turn_all_lights(alliance, on=False)


        if not CHEAT_CODE or not REVERSED_CHEAT_CODE:
            score = 100
            print("CHEAT CODE bonus")
            YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_WHACK_A_MOLE_SCORE.name, {"alliance": alliance, "score": score})) 
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
            return 
        
        if STREAK == (1 or 2):
            score = 20
        if STREAK == (3 or 4):
            score = 40
        if STREAK == (5 or 6):
            score = 60
        if STREAK >= 7:
            score = 80
            return
        YC.send((YDL_TARGETS.SHEPHERD, SHEPHERD_HEADER.UPDATE_WHACK_A_MOLE_SCORE.name, {"alliance": alliance, "score": score})) 
        print(f'score: {score}')
        print(f'alliance: {alliance}')
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
