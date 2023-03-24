import time
import random
import queue
import threading
from ydl import YDLClient
from utils import *


NUM_BUTTONS = 5
YC = YDLClient(YDL_TARGETS.SHEPHERD)
EVENT_QUEUE = queue.Queue()

CHEAT_CODE = [1, 2, 3, 4, 5, 4, 3, 2, 1] #cheat code button order
REVERSED_CHEAT_CODE = [5, 4, 3, 2, 1, 2, 3, 4, 5]


def turn_all_lights(on):
    head = SENSOR_HEADER.TURN_ON_BUTTON_LIGHT if on else SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT
    for i in range(NUM_BUTTONS):
        YC.send((YDL_TARGETS.SENSORS, head.name, {"id": i}))

def fill_queue():
    while True:
        EVENT_QUEUE.put(YC.receive()) #coming from sensors when being paused

# def start_whackamole():
#     start()

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

    #ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT.name, {"id": 1})
    #print("banana boat")
    """
    while True:
        turn_all_lights(on=False)
        time.sleep(1)
        turn_all_lights(on=True)
        time.sleep(1)
    """
    turn_all_lights(on=False)
    score = 0
    YC.send((YDL_TARGETS.UI, UI_HEADER.UPDATE_PLAYER_SCORE.name, {"score": score}))
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
        button = int(random.random()*NUM_BUTTONS)
        YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name, {"id": button}))
        
        while not EVENT_QUEUE.empty(): EVENT_QUEUE.get(True) # clear the queue (The remaining ydl calls received)
        delay = 30
        waited = 0
        pressed = False



        # while received a ydl call or we still have time
        while (not EVENT_QUEUE.empty()) or (waited < delay and not pressed):
            waited += 0.01            
            time.sleep(0.01)
            try:                
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue #go back to the top of the while loop


            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS.name:
                # print("III pressed: " + str(message[2]["id"]))
                BUTTON_ID = int(message[2]["id"])
                if BUTTON_ID == button:
                    pressed = True
                if BUTTON_ID == CHEAT_CODE[0]:
                    CHEAT_CODE.pop
                if BUTTON_ID == REVERSED_CHEAT_CODE[0]:
                    REVERSED_CHEAT_CODE.pop

        if pressed:
            #print(f"got {button} in {round(waited,2)} seconds", end=" ")
            STREAK += 1
            turn_all_lights(on=True)
            time.sleep(0.2)
            turn_all_lights(on=False)
        if not CHEAT_CODE or not REVERSED_CHEAT_CODE:
            score = 100
            print("CHEAT CODE bonus")
            YC.send((YDL_TARGETS.UI, UI_HEADER.UPDATE_PLAYER_SCORE.name, {"score": score}))
            return
        
        if STREAK == (1 or 2):
            score = 20
        if STREAK == (3 or 4):
            score = 40
        if STREAK == (5 or 6):
            score = 60
        if STREAK >= 7:
            score = 80
        YC.send((YDL_TARGETS.UI, UI_HEADER.UPDATE_PLAYER_SCORE.name, {"score": score}))

        print(f'score: {score}')
        YC.send((YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name, {"id": button}))
        YC.send((YDL_TARGETS.UI, UI_HEADER.UPDATE_PLAYER_SCORE.name, {"score": score}))
        """
        if (not pressed):
            # print("not pressed")
            YC.send((YDL_TARGETS.UI, UI_HEADER.GAME_OVER.name, { }))
        
            return
        """
        sleeptime = random.random() + 1
        time.sleep(sleeptime)

threading.Thread(target=fill_queue, args=(), daemon=True).start()
start_helper()

# EVERYWHERE_FUNCTIONS = {
#     SHEPHERD_HEADER.START_WHACKAMOLE.name: start_whackamole,
# }



