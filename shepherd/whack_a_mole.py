#!/usr/bin/python
import time
import random
import queue
import threading
from ydl import YDLClient
from utils import *

"""
Make sure to update the number of buttons used
"""
NUM_BUTTONS = 5
YC = YDLClient(YDL_TARGETS.SHEPHERD)
EVENT_QUEUE = queue.Queue()

def turn_all_lights(on):
    head = SENSOR_HEADER.TURN_ON_BUTTON_LIGHT if on else SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT
    for i in range(NUM_BUTTONS):
        YC.send((YDL_TARGETS.SENSORS, head.name, {"id": i}))

"""
Stores all of the YDL calls in EVENT_QUEUE
"""
def fill_queue():
    while True:
        EVENT_QUEUE.put(YC.receive())

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

# EVERYWHERE_FUNCTIONS = {
#     SHEPHERD_HEADER.START_WHACKAMOLE.name: start_whackamole,
# }