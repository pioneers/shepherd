from ydl import YDLClient
from utils import YDL_TARGETS, SHEPHERD_HEADER, SENSOR_HEADER
import threading

yc = YDLClient(YDL_TARGETS.SENSORS)
lights = [False] * 10

def format_lights(ar):
    return "".join([("@" if a else "-") for a in ar])

def keyboard_input():
    while True:
        line = input()
        if line in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=int(line)))


threading.Thread(target=keyboard_input, daemon=True).start()
while True:
    _, msg_header, data = yc.receive()
    if msg_header == SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name:
        lights[data['id']] = True
    else:
        lights[data['id']] = False
    print(format_lights(lights[0:5]) + " " + format_lights(lights[5:10]))