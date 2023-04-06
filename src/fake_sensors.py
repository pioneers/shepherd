from ydl import YDLClient
from utils import YDL_TARGETS, SHEPHERD_HEADER, SENSOR_HEADER
import threading

yc = YDLClient(YDL_TARGETS.SENSORS)


def keyboard_input():
    while True:
        line = input()
        if line in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=int(line)))


threading.Thread(target=keyboard_input, daemon=True).start()
while True:
    print(yc.receive())