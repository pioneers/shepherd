import time
import random
import queue
import threading
from ydl import Client
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
        if msg[1] == SHEPHERD_HEADER.BUTTON_PRESS:
            EVENT_QUEUE.put(msg)


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
            if message[1] == SHEPHERD_HEADER.START_WHACKAMOLE:
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
    interval = .5
    score = 0
    YC.send(UI_HEADER.UPDATE_PLAYER_SCORE(score))
    while True:
        # print("start score: " + str(score))
        button = int(random.random()*NUM_BUTTONS)
        YC.send(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT(button))
        
        while not EVENT_QUEUE.empty(): EVENT_QUEUE.get(True) # clear the queue, avoid vibro-tapping
        delay = random.random()/2
        delay = delay if delay > .1 else .1
        waited = 0
        pressed = False
        while (not EVENT_QUEUE.empty()) or (waited < interval and not pressed):
            waited += 0.01
            time.sleep(0.01)
            try:
                message = EVENT_QUEUE.get(False)
            except queue.Empty:
                continue  
            if message[1] == SHEPHERD_HEADER.BUTTON_PRESS:
                # print("III pressed: " + str(message[2]["id"]))
                if int(message[2]["id"]) == button:
                    pressed = True
                else:
                    break
        if pressed:
            print(f"got {button} in {round(waited,2)} seconds", end=" ")
            score += 1
            # turn_all_lights(on=True)
            # time.sleep(0.1)
            # turn_all_lights(on=False)
        else:
            print(f":( {button}", end=" ")
        print(f'score: {score}')
        YC.send(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT(button))
        YC.send(UI_HEADER.UPDATE_PLAYER_SCORE(score))
        if (not pressed):
            # print("not pressed")
            YC.send(UI_HEADER.WHACK_A_MOLE_GAME_OVER())
            return
        # sleeptime = random.random() + 1
        time.sleep(0.01)

threading.Thread(target=fill_queue, args=(), daemon=True).start()
start_helper()
