#LCM -> TURN_ON_LIGHT, {"id": 4}
#LCM -> SET_TRAFFIC_LIGHT, {"id": ???, color : "green"}

# START_BUTTON_PRESSED {} -> LCM

# figure out three things: 1) which device talking to, 2) which param of device to modify 3) value

# TURN_ON_LIGHT, {light : 7}

#arduino 1: lights [0,1,2,5,6]
#arduino 2: lights [3,4,7], traffic_light

# Dev Handler should get something in the form
# device 8, parameter 1, value 1.0

"""
LCM Messages to Sensors.py should follow this format:

[HEADER, {args}]

args: {
    id : #
    variables : values
}

Details for each header will live in Utils.py
"""

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
    # TODO: This will live in sensor_interface.py instead (maybe?)
    events = queue.Queue()
    lcm_start_read(LCM_TARGETS.SENSORS, events)
    while True:
        time.sleep(0.1)
        payload = events.get(True)
        print(payload)
        if payload[0] in HEADER_MAPPINGS:
            lowcar_message = translate_lcm_message(payload)
            place_device_command(lowcar_message)
        elif payload[0] in HEADER_COMMAND_MAPPINGS:
            HEADER_COMMAND_MAPPINGS[payload[0]](payload[1])

class Device:
    """
    An Arduino Device is connected to a number of sensors (also known as Parameter).
    It has a uuid (you get this when you flash it), type (assigned in the lowcar file),
    and parameters (mentioned above)
    SUPER IMPORTANT: make sure the sensors/shepherd_util.h header file has the same values!!
    """
    def __init__(self, device_type, uuid, parameters):
        self.uuid = uuid
        self.type = device_type
        self.parameters = parameters
        for parameter in self.parameters:
            parameter.arduino = self

class Parameter:
    """
    A parameter (sensor) consists of:
    - a name
        - this is the name of the sensor. Under the hood, this is the name of a variable being shared with the arduino.
        - this needs to be the same as the name in shepherd_utils.c
    - an identifier
        - this is the number to identify this sensor in shepherd. This is used internally for abstraction with the rest of shepherd.
        - this should be unique
        - this can be optional
    example: name light, identifier: 1 means light 1.
             this corresponds to the "id" in the LCM header args: { id : 1, variables : values}
    - a parent device (arduino) that owns this sensor
    """
    def __init__(self, name, identifier=None, debounce_threshold=None):
        self.name = name
        self.identifier = identifier
        self.__device = None
        self.debounce_threshold = None
        # LCM target
        # LCM header

    @property
    def device(self):
        if self.__device is None:
            raise Exception("Arduino is none, but is being accessed :(")
        return self.__device

    @device.setter
    def device(self, d):
        self.__device = d

    def value_from_header(self, header):
        """
        Returns the value to write to this device. For example,
        light on should correspond to a value of 1.0
        """
        raise Exception("override this function plz")
    
    def is_state_change_significant(self, value: float, previous_value: float):
        raise Exception("override this function you sad little sheep")
    
    def lcm_message_from_state_change(self, value: float):
        # feel free to add previous_value as a param if needed
        raise Exception("override this function you sad little sheep")

    def __str__(self):
        return f"Device({self.name}, {self.identifier})"

def parameter_from_header(header):
    sensor_pool = HEADER_MAPPINGS[header[0]]
    args = header[1]
    for p in sensor_pool:
        if not p.identifier or args.get("id", None) == p.identifier:
            return p
    raise Exception(f'no device found associated with LCM header {header}')

def translate_lcm_message(header):
    """
    This method will decode three import pieces of information:
    1) the arduino and device to talk to
    2) the parameter of device to modify
    3) the value to modify it to
    """
    parameter = parameter_from_header(header)
    device = f'{parameter.device.type}_{parameter.device.identifier}'
    value = parameter.value_from_header(header)
    message = LowcarMessage([device], [{parameter.identifier:value}])
    return message

################################################
# Game Specific Variables
################################################

class Light(Parameter):
    def value_from_header(self, header):
        if header[0] == SENSOR_HEADER.TURN_ON_LIGHT:
            return 1.0
        elif header[0] == SENSOR_HEADER.TURN_OFF_LIGHT:
            return 0.0
        raise Exception(f"Attempting to get value of light, but header[0] is {header[0]}")
        
class Button(Parameter):
    def is_state_change_significant(self, value: float, previous_value: float):
        if value == 1.0 and previous_value == 0.0:
            return True
        return False

    def lcm_message_from_state_change(self, value: float): 
        lcm_send()

class TrafficLight(Parameter):
    COLORS = {"red" : 0xFF0000, "green" : 0x00FF00, "yellow" : 0xFFFF00}

    def value_from_header(self, header):
        if header[0] == SENSOR_HEADER.SET_TRAFFIC_LIGHT:
            return self.COLORS[header[1]["color"]]
        raise Exception(f"Attempting to get value of traffic light but header[0] is {header[0]}")

lights = [Light(name=f"light{i}", identifier=i) for i in range(8)]
traffic_lights = [TrafficLight("traffic_light")]

arduino_1 = Device(1, 1, [lights[0], lights[1], lights[2], lights[5], lights[7]])
arduino_2 = Device(2, 2, [lights[3], lights[4], lights[7], traffic_lights[0]])

################################################
# Evergreen Variables (still need to be updated)
################################################

HEADER_MAPPINGS = {
    SENSOR_HEADER.TURN_ON_LIGHT : lights,
    SENSOR_HEADER.TURN_OFF_LIGHT : lights,
    SENSOR_HEADER.SET_TRAFFIC_LIGHT : traffic_lights
}

HEADER_COMMAND_MAPPINGS = {

}

arduinos = [arduino_1, arduino_2]

################################################

if __name__ == '__main__':
    start()