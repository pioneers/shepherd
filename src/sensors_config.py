import time
from ydl import Client
from utils import *
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers

low = DigitalValue.LOW.value
high = DigitalValue.HIGH.value
arduino1 = Arduino(1)
arduino2 = Arduino(2)

YC = Client(YDL_TARGETS.SENSORS)

lights = [
    OutputPin(arduino1, 10, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 9, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 7, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 5, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 3, PinMode.DIGITAL_OUT, initial_value=high),

    OutputPin(arduino2, 16, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 9, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 7, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 5, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 3, PinMode.DIGITAL_OUT, initial_value=high)
]


def make_button_handler(id):
    def handler(state):
        if state == low:
            print(f"button {id} was pressed: {state}")
            YC.send(SHEPHERD_HEADER.BUTTON_PRESS(id=id))
    return handler

buttons = [
    InputPin(arduino1, 16, PinMode.DIGITAL_IN, make_button_handler(0)),
    InputPin(arduino1, 8, PinMode.DIGITAL_IN, make_button_handler(1)),
    InputPin(arduino1, 6, PinMode.DIGITAL_IN, make_button_handler(2)),
    InputPin(arduino1, 4, PinMode.DIGITAL_IN, make_button_handler(3)),
    InputPin(arduino1, 2, PinMode.DIGITAL_IN, make_button_handler(4)),

    InputPin(arduino2, 10, PinMode.DIGITAL_IN, make_button_handler(5)),
    InputPin(arduino2, 8, PinMode.DIGITAL_IN, make_button_handler(6)),
    InputPin(arduino2, 6, PinMode.DIGITAL_IN, make_button_handler(7)),
    InputPin(arduino2, 4, PinMode.DIGITAL_IN, make_button_handler(8)),
    InputPin(arduino2, 2, PinMode.DIGITAL_IN, make_button_handler(9))
]
# color_sensor = InputPin(arduino1, 123, PinMode.PULSE_IN, banana)

start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(5)], # CHANGE THIS IF NOT ON LINUX
    [arduino1, arduino2]
)



while True:
    msg = YC.receive()
    print(msg)
    if msg[1] == "turn_on_button_light":
        lights[msg[2]["id"]].set_state(high)
    else:
        lights[msg[2]["id"]].set_state(low)
