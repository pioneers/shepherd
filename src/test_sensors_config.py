import time
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers

low = DigitalValue.LOW.value
high = DigitalValue.HIGH.value
arduino1 = Arduino(1)
arduino2 = Arduino(2)
arduino3 = Arduino(3)
arduino4 = Arduino(4)


lights = [
    OutputPin(arduino1, 3, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 5, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 7, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 9, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino1, 16, PinMode.DIGITAL_OUT, initial_value=high),

    OutputPin(arduino2, 3, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 5, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 7, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 9, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino2, 16, PinMode.DIGITAL_OUT, initial_value=high),
]

sails = [
    OutputPin(arduino3, 6, PinMode.DIGITAL_OUT, initial_value=high), # Blue alliance sail CW (not tested)
    OutputPin(arduino3, 7, PinMode.DIGITAL_OUT, initial_value=high), # Blue alliance sail CCW (not tested)
    OutputPin(arduino4, 6, PinMode.DIGITAL_OUT, initial_value=high), # Blue alliance sail CW (not tested)
    OutputPin(arduino4, 7, PinMode.DIGITAL_OUT, initial_value=high), # Blue alliance sail CCW (not tested)
]


def make_button_handler(id):
    def handler(state):
        print(f"button {id} was pressed: {state}")
    return handler

buttons = [
    InputPin(arduino1, 2, PinMode.DIGITAL_IN, make_button_handler(0)),
    InputPin(arduino1, 4, PinMode.DIGITAL_IN, make_button_handler(1)),
    InputPin(arduino1, 6, PinMode.DIGITAL_IN, make_button_handler(2)),
    InputPin(arduino1, 8, PinMode.DIGITAL_IN, make_button_handler(3)),
    InputPin(arduino1, 10, PinMode.DIGITAL_IN, make_button_handler(4)),
   
    InputPin(arduino2, 2, PinMode.DIGITAL_IN, make_button_handler(0)),
    InputPin(arduino2, 4, PinMode.DIGITAL_IN, make_button_handler(1)),
    InputPin(arduino2, 6, PinMode.DIGITAL_IN, make_button_handler(2)),
    InputPin(arduino2, 8, PinMode.DIGITAL_IN, make_button_handler(3)),
    InputPin(arduino2, 10, PinMode.DIGITAL_IN, make_button_handler(4)),
]
# color_sensor = InputPin(arduino1, 123, PinMode.PULSE_IN, banana)

start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(10)], # CHANGE THIS IF NOT ON LINUX
    [arduino1, arduino2, arduino3, arduino4]
)

while True:
    command = input()
    if command == "a":
        sails[2].set_state(low);
        print("hh")
        #for light in lights:
        #    light.set_state(high)
    elif command == "b":
        sails[2].set_state(high);
        print("hl")
    else:
        sails[0].set_state(high);
        for light in lights:
            light.set_state(low)
    print("asd")