from ydl import Client, Handler
from utils import *


yc = Client(YDL_TARGETS.SHEPHERD)
yh = Handler()
NUM_OF_LIGHTS = 3
lights = [False for _ in range(NUM_OF_LIGHTS)]
_print = True


@yh.on(SHEPHERD_HEADER.TURN_ON_BUTTON_LIGHT)
def turn_on_button_light(id: int):
    lights[id] = True

@yh.on(SHEPHERD_HEADER.TURN_OFF_BUTTON_LIGHT)
def turn_off_button_light(id: int):
    lights[id] = False


while True:
    if (_print):
        _print = False
        print(''.join(["          " + ("@" if lights[n] else "-") for n in range(NUM_OF_LIGHTS)]))
    msg = yc.receive()
    _print = yh.handle(msg)
