#LCM -> TURN_ON_LIGHT, {light: 7}
#LCM -> SET_TRAFFIC_LIGHT, {color: "green"}

# START_BUTTON_PRESSED {} -> LCM

# figure out three things: 1) which device talking to, 2) which param of device to modify 3) value

# TURN_ON_LIGHT, {light: 7}

#arduino 1: lights [0,1,2,5,6]
#arduino 2: lights [3,4,7], traffic_light

# Dev Handler should get something in the form
# device 8, parameter 1, value 1.0

from Utils import *
import queue
from LCM import *
import time

################################################
# Evergreen Methods
################################################

def start():
    """
    Main loop which processes the event queue.
    """
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.SENSORS, events)
    while True:
        time.sleep(0.1)
        payload = events.get(True)
        print(payload)
        receive_lcm_message(payload)

class Arduino:
    """
    An Arduino is connected to a number of devices.
    """
    def __init__(self, uuid, devices):
        self.uuid = uuid
        self.devices = devices
        for device in self.devices:
            device.arduino = self

    def get_param(self, device):
        if device in self.devices:
            return self.devices.index(device)

        raise Exception(f"arduino does not contain device {device}")

class Device:
    """
    A device consists of:
    - a name (such as `light`)
    - an identifer (TODO: MATT CAN YOU DESCIBE THIS)
    - a parent arduino that owns this device
    """
    def __init__(self, name=None, identifier=None):
        self.name = name
        self.identifier = identifier
        self.__arduino = None
        if name and identifier is None or identifier and name is None:
            raise Exception("if name is not none, identifier should not be none, and vice versa")

    @property
    def arduino(self):
        if self.__arduino is None:
            raise Exception("Arduino is none, but is being accessed :(")
        return self.__arduino

    @arduino.setter
    def arduino(self, a):
        self.__arduino = a

    def value_from_header(self, header):
        """
        Returns the value to write to this device. For example, 
        light on should correspond to a value of 1.0
        """
        raise Exception("override this function plz")

    def __str__(self):
        return f"Device({self.name}, {self.identifier})"

def device_from_header(header):
    device_pool = HEADER_MAPPINGS[header[0]]
    args = header[1]
    device = None
    for d in device_pool:
        if not d.name or args.get(d.name, None) == d.identifier:
            device = d
            break
    return device

def receive_lcm_message(header):
    """
    This method will decode three import pieces of information:
    1) the arduino and device to talk to
    2) the parameter of device to modify
    3) the value to modify it to
    """
    device = device_from_header(header)
    arduino = device.arduino
    param = arduino.get_param(device)
    value = device.value_from_header(header)
    #TODO call sensor_interface.py here

################################################
# Game Specific Variables
################################################

class Light(Device):
    def value_from_header(self, header):
        if header[0] == SENSOR_HEADER.TURN_ON_LIGHT:
            return 1.0
        elif header[0] == SENSOR_HEADER.TURN_OFF_LIGHT:
            return 0.0
        raise Exception(f"Attempting to get value of light, but header[0] is {header[0]}")

class TrafficLight(Device):
    COLORS = {"red" : 0xFF0000, "green" : 0x00FF00, "yellow" : 0xFFFF00}

    def value_from_header(self, header):
        if header[0] == SENSOR_HEADER.SET_TRAFFIC_LIGHT:
            return self.colors[header[1]["color"]]
        raise Exception(f"Attempting to get value of traffic light but header[0] is {header[0]}")

lights = [Light(name="light", identifier=i) for i in range(8)]
traffic_lights = [Device()]

arduino_1 = Arduino(ARDUINO_UUIDS.ARDUINO_1, [lights[0], lights[1], lights[2], lights[5], lights[7]])
arduino_2 = Arduino(ARDUINO_UUIDS.ARDUINO_2, [lights[3], lights[4], lights[7], traffic_lights[0]])

################################################
# Evergreen Variables (still need to be updated)
################################################

HEADER_MAPPINGS = {
SENSOR_HEADER.TURN_ON_LIGHT : lights,
SENSOR_HEADER.TURN_OFF_LIGHT : lights,
SENSOR_HEADER.SET_TRAFFIC_LIGHT : traffic_lights
}

arduinos = [arduino_1, arduino_2]

################################################

if __name__ == '__main__':
    start()
_