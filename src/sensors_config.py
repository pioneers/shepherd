import time
from ydl import Client, Handler
from utils import *
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers
import threading

blueSail = False
goldSail = False

low = DigitalValue.LOW.value
high = DigitalValue.HIGH.value
arduino1 = Arduino(1)
arduino2 = Arduino(2)
arduino3 = Arduino(3)
arduino4 = Arduino(4)
arduino5 = Arduino(5)
arduino6 = Arduino(6)
YC = Client(YDL_TARGETS.SENSORS)
yh = Handler()

lights = [
    # OutputPin(arduino1, 3, PinMode.DIGITAL_OUT, initial_value=high),
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
    OutputPin(arduino3, 6, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino3, 7, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino4, 6, PinMode.DIGITAL_OUT, initial_value=high),
    OutputPin(arduino4, 7, PinMode.DIGITAL_OUT, initial_value=high),
]

##add a rfid sensor output pins (2 i guess)

walls = [
    OutputPin(arduino5, 20, PinMode.DIGITAL_OUT, initial_value=high)
    OutputPin(arduino5, 21, PinMode.DIGITAL_OUT, initial_value=high)
    OutputPin(arduino6, 20, PinMode.DIGITAL_OUT, initial_value=high)
    OutputPin(arduino6, 21, PinMode.DIGITAL_OUT, initial_value=high)
]

rfid = [
    InputPin(arduino1, 8, PinMode.DIGITAL_IN, lambda: print("wow we see something!"))
]

def make_button_handler(id):
    def handler(state):
        if state == low:
            print(f"button {id} was pressed: {state}")
            YC.send(SHEPHERD_HEADER.BUTTON_PRESS(id=id))
    return handler



buttons = [
    InputPin(arduino1, 2, PinMode.DIGITAL_IN, make_button_handler(0)),
    InputPin(arduino1, 4, PinMode.DIGITAL_IN, make_button_handler(1)),
    InputPin(arduino1, 6, PinMode.DIGITAL_IN, make_button_handler(2)),
    InputPin(arduino1, 8, PinMode.DIGITAL_IN, make_button_handler(3)),
    InputPin(arduino1, 10, PinMode.DIGITAL_IN, make_button_handler(4)),
   
    InputPin(arduino2, 2, PinMode.DIGITAL_IN, make_button_handler(5)),
    InputPin(arduino2, 4, PinMode.DIGITAL_IN, make_button_handler(6)),
    InputPin(arduino2, 6, PinMode.DIGITAL_IN, make_button_handler(7)),
    InputPin(arduino2, 8, PinMode.DIGITAL_IN, make_button_handler(8)),
    InputPin(arduino2, 10, PinMode.DIGITAL_IN, make_button_handler(9)),

]



# color_sensor = InputPin(arduino1, 123, PinMode.PULSE_IN, banana)

start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(10)],  # CHANGE THIS IF NOT ON LINUX
    [arduino1, arduino2, arduino3, arduino4]
)


@yh.on(SENSOR_HEADER.TURN_ON_BUTTON_LIGHT)
def turn_on_button_light(id):
    print("turn the light on")
    lights[id].set_state(high)


@yh.on(SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT)
def turn_off_button_light(id):
    print("turn the light off")
    lights[id].set_state(low)

def lower_sail_thread(alliance):
    global blueSail, goldSail
    print("THIS GOT RAN")
    if alliance == ALLIANCE_COLOR.BLUE and not blueSail:
        print("LOWER Inner Function ran blue")
        sails[1].set_state(low)
        time.sleep(1.5)
        sails[1].set_state(high)
        blueSail = True
    elif alliance == ALLIANCE_COLOR.GOLD and not goldSail:
        print("LOWER Inner Function ran gold")
        sails[2].set_state(low)
        time.sleep(1.5)
        sails[2].set_state(high)
        goldSail = True

def raise_sail_thread(alliance):
    global blueSail, goldSail
    print("THIS GOT RAN")
    if alliance == ALLIANCE_COLOR.BLUE and blueSail:
        print("LOWER Inner Function ran blue")
        blueSail = False
        sails[0].set_state(low)
        time.sleep(1.5)
        sails[0].set_state(high)
    elif alliance == ALLIANCE_COLOR.GOLD and goldSail:
        print("LOWER Inner Function ran gold")
        goldSail = False
        sails[3].set_state(low)
        time.sleep(1.5)
        sails[3].set_state(high)


@yh.on(SENSOR_HEADER.LOWER_SAIL)
def lower_sail(alliance):
    print("Outer Function Ran")
    t = threading.Thread(target=lower_sail_thread, args=[alliance])
    t.run()
    

@yh.on(SENSOR_HEADER.RAISE_SAIL)
def raise_sail(alliance):
    print("Outer Function Ran")
    t = threading.Thread(target=raise_sail_thread, args=[alliance])
    t.run()

while True:
    msg = YC.receive()
    yh.handle(msg)
    print(msg)
    # if msg[1] == "turn_on_button_light":
    #     turn_on_button_light(msg[2]["id"])

    # else:
    #     turn_off_button_light(msg[2]["id"])

    #TO ADD FOR RFID
        #sensor on -- turn sensor on(id for alliance)

    
