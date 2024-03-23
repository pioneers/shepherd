from ydl import Client, Handler
from utils import YDL_TARGETS, SHEPHERD_HEADER, SENSOR_HEADER
import threading

yc = Client(YDL_TARGETS.SENSORS)
num_lights = 12
lights = [False] * num_lights
yh = Handler()


def format_lights(ar):
    return "".join([("@" if a else "-") for a in ar])


def keyboard_input():
    while True:
        line = input()
        if line in [str(n) for n in range(12)]:
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=int(line)))


@yh.on(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT)
def turn_on_button_light(id):
    lights[id] = True


@yh.on(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT)
def turn_off_button_light(id):
    lights[id] = False


threading.Thread(target=keyboard_input, daemon=True).start()
print(format_lights(lights[0: num_lights//2]) + " " +
      format_lights(lights[num_lights//2: num_lights]))
while True:
    msg = yc.receive()
    yh.handle(msg)
    # _, msg_header, data = yc.receive()
    # if msg_header == SENSOR_HEADER.TURN_ON_BUTTON_LIGHT:
    #     lights[data['id']] = True
    # else:
    #     lights[data['id']] = False
    print(format_lights(lights[0: num_lights//2]) + " " +
          format_lights(lights[num_lights//2: num_lights]))
