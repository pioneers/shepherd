from ydl import Client, Handler
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers
from utils import YDL_TARGETS, SHEPHERD_HEADER, SENSOR_HEADER


yc = Client(YDL_TARGETS.SENSORS)
yh = Handler()
arduino1 = Arduino(1)
arduino2 = Arduino(2)
dummy_arduino = Arduino(123456)
high = DigitalValue.HIGH.value
low = DigitalValue.LOW.value

def make_button_handler(id):
    def handler(state):
        if state == DigitalValue.HIGH.value:
            print(f"Button {id} was pressed!")
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=id))
    return handler

def make_linebreak_handler(id):
    def handler(state):
        if state == DigitalValue.LOW.value:
            print(f"Linebreak {id} was crossed!")
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=100000+id)) # TODO: add actual linebreak header
    return handler

lights = [
    OutputPin(arduino1, 3, PinMode.DIGITAL_OUT, initial_value=low), # button lights
    OutputPin(arduino1, 5, PinMode.DIGITAL_OUT, initial_value=low), # corner lights
    OutputPin(arduino2, 3, PinMode.DIGITAL_OUT, initial_value=low), # button lights
    OutputPin(arduino2, 5, PinMode.DIGITAL_OUT, initial_value=low), # corner lights
    OutputPin(arduino1, 7, PinMode.DIGITAL_OUT, initial_value=low), # midline lights
    OutputPin(arduino2, 7, PinMode.DIGITAL_OUT, initial_value=low), # midline lights
]
buttons = [
    InputPin(arduino1, 2, PinMode.DIGITAL_IN, make_button_handler(0)), # button
    InputPin(arduino2, 2, PinMode.DIGITAL_IN, make_button_handler(1)), # button
]
lasers = [
    OutputPin(dummy_arduino, 2, PinMode.DIGITAL_OUT, initial_value=low), # example laser
]
linebreaks = [
    InputPin(dummy_arduino, 10, PinMode.PULSE_IN, make_linebreak_handler(5)) # example linebreak
]

start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(5)],
    [arduino1, arduino2]
)

@yh.on(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT)
def set_high(id):
    lights[id].set_state(high)

@yh.on(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT)
def set_low(id):
    lights[id].set_state(low)

while True:
    data = yc.receive()
    yh.handle(data)
