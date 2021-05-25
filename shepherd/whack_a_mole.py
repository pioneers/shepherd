#!/usr/bin/python
import time
import random
import queue
from YDL import *
from Utils import *
def start():
    for i in range(7):
        ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {"id": i})
    event_queue = queue.Queue()
    ydl_start_read(YDL_TARGETS.SHEPHERD, event_queue)
    score = 0
    while True:
        button = int(random.random()*6)
        ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, {"id": button})
        
        delay = random.random()
        delay = delay if delay > .1 else .1
        time.sleep(delay * 2)
        pressed = False
        while not event_queue.empty():
            message = event_queue.get(True)
            if message[0] == SHEPHERD_HEADER.DEHYDRATION_BUTTON_PRESS:
                if int(message[1]["button"]) == button:
                    pressed = True
        if pressed:
            ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_FIRE_LIGHT)
            score += 1
        else:
            ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_FIRE_LIGHT)
        print(f'score: {score}')
        ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {"id": button})
        time.sleep(4)

start()
