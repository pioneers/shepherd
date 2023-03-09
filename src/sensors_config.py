"""
Sensors code for Spring 2023. Has the following devices:
 - arduino1
    - whack-a-mole game (5 buttons, 5 lights, timers)
    - traffic light
 - arduino2
    - whack-a-mole game (5 buttons, 5 lights, timers)
    - traffic light
 - arduino3
    - a button light (don't actually care about the button)
 - arduino4
    - a button light (don't actually care about the button)

The whack-a-mole makes things more complex, because it needs to handle:
 - random buttons light up every 30 seconds or until pressed, whichever comes first
 - at any point, player may enter a "cheat code" which makes the wall light up
"""

import time
import random
import threading
import queue
from ydl import YDLClient
from timer import TimerGroup, Timer
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers
from utils import YDL_TARGETS, SHEPHERD_HEADER, SENSOR_HEADER


arduino1 = Arduino(1)
arduino2 = Arduino(2)
arduino3 = Arduino(3)
arduino4 = Arduino(4)
high = DigitalValue.HIGH.value
low = DigitalValue.LOW.value

timers = TimerGroup()


class WhackAMoleGame:
    def __init__(self, arduino: Arduino):
        self.arduino = arduino
        self.buttons = [
            InputPin(arduino, 2, PinMode.DIGITAL_IN, self.make_button_handler(0)),
            InputPin(arduino, 3, PinMode.DIGITAL_IN, self.make_button_handler(1)),
            InputPin(arduino, 4, PinMode.DIGITAL_IN, self.make_button_handler(2)),
            InputPin(arduino, 5, PinMode.DIGITAL_IN, self.make_button_handler(3)),
            InputPin(arduino, 6, PinMode.DIGITAL_IN, self.make_button_handler(4))
        ]
        self.lights = [
            OutputPin(arduino, 7, PinMode.DIGITAL_OUT, low),
            OutputPin(arduino, 7, PinMode.DIGITAL_OUT, low),
            OutputPin(arduino, 7, PinMode.DIGITAL_OUT, low),
            OutputPin(arduino, 7, PinMode.DIGITAL_OUT, low),
            OutputPin(arduino, 7, PinMode.DIGITAL_OUT, low)
        ]
        self.chosen_button = None
        self.last_pressed = [None] * 10
        self.light_events = queue.Queue()
        self.expire_timer = Timer(timers, self.do_expire)
        self.choose_timer = Timer(timers, self.do_choose)
        threading.Thread(target=self.run_loop, daemon=True).start()


    def make_button_handler(self, id):
        def handler(state):
            """
            Handles a button press. If cheat code, flash buttons, otherwise, whack
            """
            if state == high:
                print(f"button {id} on arduino {self.arduino.uuid} was pressed. history: {self.last_pressed}")
                self.last_pressed = self.last_pressed[1:] + [id]
                cheat_code = [0, 1, 2, 3, 4, 4, 3, 2, 1, 0]
                if self.last_pressed == cheat_code:
                    print("cheat code")
                    self.light_events.put(("flash", sum(([x, x] for x in cheat_code), start=[])))
                if id == self.chosen_button:
                    print("correct button press")
                    self.light_events.put(("flash", [id] * 6))
                    self.light_events.put(("off", id))
                    self.do_choose()
                else:
                    print(f"incorrect button press: correct is {self.chosen_button}")
                    self.do_expire()
        return handler

    def do_expire(self):
        print(f"time expired on game {self.arduino.uuid}")
        if self.chosen_button is not None:
            self.light_events.put(("off", self.chosen_button))
        self.chosen_button = None
        self.choose_timer.start(10)
        self.expire_timer.reset()

    def do_choose(self):
        new_choice = self.chosen_button
        while new_choice == self.chosen_button:
            new_choice = random.randint(0, 4) # inclusive of both ends
        self.chosen_button = new_choice
        print(f"choosing button {self.chosen_button} on {self.arduino.uuid}")
        self.light_events.put(("on", self.chosen_button))
        self.choose_timer.reset()
        self.expire_timer.start(30)

    def run_loop(self):
        while True:
            event = self.light_events.get()
            print(f"doing event {event} on arduino {self.arduino.uuid}")
            if event[0] == "off":
                self.lights[event[1]].set_state(low)
            elif event[0] == "on":
                self.lights[event[1]].set_state(high)
            elif event[0] == "flash":
                old_states = [light.state for light in self.lights]
                for light in self.lights:
                    light.set_state(low)
                for i in event[1]: # toggle each light in the list
                    other = high if self.lights[i].state == low else low
                    self.lights[i].set_state(other)
                    time.sleep(0.1)
                for (old_state, light) in zip(old_states, self.lights):
                    light.set_state(old_state)
            else:
                print("uh oh spighettio")

    def start(self):
        self.light_events.put(("flash", [0, 1, 2, 3, 4] * 2))
        self.do_choose()

    def reset(self):
        """
        This has a race condition because do_choose or do_expire might happen
        after, but meh idc
        """
        self.choose_timer.reset()
        self.expire_timer.reset()
        self.chosen_button = None
        self.last_pressed = [None] * 10
        for light in self.lights:
            light.set_state(low)


game1 = WhackAMoleGame(arduino1)
game2 = WhackAMoleGame(arduino2)

traffic1 = OutputPin(arduino1, 123, PinMode.DIGITAL_OUT, low)
traffic2 = OutputPin(arduino2, 123, PinMode.DIGITAL_OUT, low)

blight1 = OutputPin(arduino3, 123, PinMode.DIGITAL_OUT, low)
blight2 = OutputPin(arduino4, 123, PinMode.DIGITAL_OUT, low)


def start_everything():
    game1.start()
    game2.start()
    traffic1.set_state(high)
    traffic2.set_state(high)
    blight1.set_state(high)
    blight2.set_state(high)

def stop_everything():
    game1.reset()
    game2.reset()
    traffic1.set_state(low)
    traffic2.set_state(low)
    blight1.set_state(low)
    blight2.set_state(low)




def keyboard_input():
    while True:
        line = input()
        if line == "start":
            start_everything()
        elif line == "stop":
            stop_everything()
        else:
            print("bad command")


threading.Thread(target=keyboard_input, daemon=True).start()

start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(5)],
    [arduino1, arduino2, arduino3, arduino4]
)

yc = YDLClient(YDL_TARGETS.SENSORS)
while True:
    _, header_name, _ = yc.receive()
    # TODO: stuff
