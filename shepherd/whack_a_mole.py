#!/usr/bin/python
import time
import random
import queue
from ydl import ydl_send, ydl_start_read
from utils import *


NUM_BUTTONS = 7


def turn_all_lights(on):
    head = SENSOR_HEADER.TURN_ON_LIGHT if on else SENSOR_HEADER.TURN_OFF_LIGHT
    for i in range(NUM_BUTTONS):
        ydl_send(YDL_TARGETS.SENSORS, head.name, {"id": i})    

def start():

    #ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT.name, {"id": 1})
    #print("banana boat")
    turn_all_lights(on=False)
    event_queue = queue.Queue()
    ydl_start_read(YDL_TARGETS.SHEPHERD, event_queue)
    score = 0
    while True:
        button = int(random.random()*NUM_BUTTONS)
        ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT.name, {"id": button})
        
        while not event_queue.empty(): event_queue.get(True) # clear the queue 
        delay = random.random()
        delay = delay if delay > .25 else .25
        time.sleep(delay)
        pressed = False
        while not event_queue.empty():
            message = event_queue.get(True)
            if message[0] == SHEPHERD_HEADER.DEHYDRATION_BUTTON_PRESS.name:
                if int(message[1]["button"]) == button:
                    pressed = True
        if pressed:
            print(f"got {button}", end=" ")
            score += 1
            turn_all_lights(on=True)
            time.sleep(0.1)
            turn_all_lights(on=False)
        else:
            print(f":( {button}", end=" ")
        print(f'score: {score}')
        ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT.name, {"id": button})
        sleeptime = random.random() + 1
        time.sleep(sleeptime)

start()
