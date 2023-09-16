from ydl import YDLClient
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers
from utils import YDL_TARGETS, SHEPHERD_HEADER, SENSOR_HEADER


yc = YDLClient(YDL_TARGETS.SENSORS)
arduino1 = Arduino(1)
high = DigitalValue.HIGH.value
low = DigitalValue.LOW.value

def make_button_handler(id):
    def handler(state):
        if state == DigitalValue.HIGH.value:
            print(f"Button {id} was pressed!")
            yc.send(SHEPHERD_HEADER.BUTTON_PRESS(id=id))
    return handler

lights = [
    OutputPin(arduino1, 3, PinMode.DIGITAL_OUT, initial_value=low), # button lights
    OutputPin(arduino1, 5, PinMode.DIGITAL_OUT, initial_value=low), # corner lights
    OutputPin(arduino1, 7, PinMode.DIGITAL_OUT, initial_value=low), # button lights
    OutputPin(arduino1, 9, PinMode.DIGITAL_OUT, initial_value=low), # button lights
    OutputPin(arduino1, 10, PinMode.DIGITAL_OUT, initial_value=low), # button lights
]
buttons = [
    InputPin(arduino1, 2, PinMode.DIGITAL_IN, make_button_handler(0)), # button
    InputPin(arduino1, 4, PinMode.DIGITAL_IN, make_button_handler(1)), # button
    InputPin(arduino1, 6, PinMode.DIGITAL_IN, make_button_handler(2)), # button
    InputPin(arduino1, 8, PinMode.DIGITAL_IN, make_button_handler(3)), # button
    InputPin(arduino1, 16, PinMode.DIGITAL_IN, make_button_handler(4)), # button
]

start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(5)],
    [arduino1]
)

incoming_headers = {
    SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name: lambda id: lights[id].set_state(high),
    SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name: lambda id: lights[id].set_state(low),
}

while True:
    _, header_name, args = yc.receive()
    if header_name in incoming_headers:
        print(f"Processing {(header_name, args)}")
        incoming_headers[header_name](**args)
    else:
        print(f"Unknown header: {(header_name, args)}")
