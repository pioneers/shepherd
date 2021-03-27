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
from __future__ import annotations
from Utils import *
import queue
from LCM import *
import time
from sensors.lowcar_message import LowcarMessage

################################################
# Evergreen Methods
################################################

class Device:
    """
    An Arduino Device is connected to a number of sensors (also known as Parameter).
    It has a uuid (you get this when you flash it), type (assigned in the lowcar file),
    and parameters (mentioned above)
    SUPER IMPORTANT: make sure the sensors/shepherd_util.h header file has the same values!!
    """
    def __init__(self, device_type, uuid, parameters: list):
        self.uuid = uuid
        self.type = device_type
        self.params = { parameter.name: parameter for parameter in parameters }
        self.polling_parameters = []
        for parameter in parameters:
            parameter.arduino = self
            if parameter.should_poll:
                self.polling_parameters.append(parameter)

    def get_identifier(self):
        return f"{self.uuid}_{self.type}"

    def get_param(self, param: str) -> Parameter:
        """
        Returns Parameter with name `param`.
        """
        if param not in self.params:
            raise Exception("Parameter {param} not found in arduino {self}")
        self.params.get(param)
    
    def __str__(self):
        return self.get_identifier()

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
    def __init__(self, name: str, should_poll: bool, identifier=None, debounce_threshold=None, lcm_header=None):
        self.name = name
        self.should_poll = should_poll
        self.identifier = identifier
        self.__device = None
        self.debounce_threshold = None
        self.lcm_header = lcm_header
        previous_parameter_values[self] = None # TODO: is it ok to init this to None

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
    
previous_parameter_values = {} # TODO: where should we put this?

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
        
class DehydrationButton(Parameter):
    def is_state_change_significant(self, value: float, previous_value: float):
        if value == 1.0 and previous_value == 0.0:
            return True
        return False

    def lcm_message_from_state_change(self, value: float):
        # fire lever, traffic button
        args = {
            "button": self.identifier
        }
        return args
        # not here
        # lcm_send(LCM_TARGETS.SHEPHERD, SHEPHERD_HEADER.DEHYDRATION_BUTTON_PRESS, ..)
        # self.identifier is which button
    
class GenericButton(Parameter):
    def is_state_change_significant(self, value: float, previous_value: float):
        if value == 1.0 and previous_value == 0.0:
            return True
        return False

    def lcm_message_from_state_change(self, value: float):
        # fire lever, traffic button
        args = {}
        return args

class TrafficLight(Parameter):
    COLORS = {"red" : 0xFF0000, "green" : 0x00FF00, "yellow" : 0xFFFF00}

    def value_from_header(self, header):
        if header[0] == SENSOR_HEADER.SET_TRAFFIC_LIGHT:
            return self.COLORS[header[1]["color"]]
        raise Exception(f"Attempting to get value of traffic light but header[0] is {header[0]}")

linebreak_debounce_threshold = 10

city_linebreak = GenericButton(name="city_linebreak", should_poll=True, identifier=0, lcm_header=SHEPHERD_HEADER.CITY_LINEBREAK, debounce_threshold=linebreak_debounce_threshold)
traffic_linebreak = GenericButton(name="traffic_linebreak", should_poll=True, identifier=1, lcm_header=SHEPHERD_HEADER.STOPLIGHT_CROSS, debounce_threshold=linebreak_debounce_threshold)
desert_linebreak = GenericButton(name="desert_linebreak", should_poll=True, identifier=2, lcm_header=SHEPHERD_HEADER.DESERT_ENTRY, debounce_threshold=linebreak_debounce_threshold)
dehydration_linebreak = GenericButton(name="dehydration_linebreak", should_poll=True, identifier=3, lcm_header=SHEPHERD_HEADER.DEHYDRATION_ENTRY, debounce_threshold=linebreak_debounce_threshold)
hypothermia_linebreak = GenericButton(name="hypothermia_linebreak", should_poll=True, identifier=4, lcm_header=SHEPHERD_HEADER.HYPOTHERMIA_ENTRY, debounce_threshold=linebreak_debounce_threshold)
airport_linebreak = GenericButton(name="airport_linebreak", should_poll=True, identifier=5, lcm_header=SHEPHERD_HEADER.FINAL_ENTRY, debounce_threshold=linebreak_debounce_threshold)

fire_lever = GenericButton(name="fire_lever", should_poll=True, lcm_header=SHEPHERD_HEADER.FIRE_LEVER)

traffic_button = GenericButton(name="traffic_button", should_poll=True, lcm_header=SHEPHERD_HEADER.STOPLIGHT_BUTTON_PRESS)
traffic_lights = [TrafficLight(name="traffic_light", should_poll=False)]

num_dehydration_buttons = 8

dehydration_buttons = [DehydrationButton(name=f"light{i}", should_poll=True, identifier=i, lcm_header=SHEPHERD_HEADER.DEHYDRATION_BUTTON_PRESS) for i in range(num_dehydration_buttons)]
lights = [Light(name=f"light{i}", should_poll=False, identifier=i) for i in range(num_dehydration_buttons)]


arduino_1 = Device(1, 1, [lights[0], lights[1], lights[2], lights[5], lights[7]])
arduino_2 = Device(2, 2, [lights[3], lights[4], lights[7], traffic_lights[0]])

################################################
# Evergreen Variables (may still need to be updated)
################################################

HEADER_MAPPINGS = {
    SENSOR_HEADER.TURN_ON_LIGHT : lights,
    SENSOR_HEADER.TURN_OFF_LIGHT : lights,
    SENSOR_HEADER.SET_TRAFFIC_LIGHT : traffic_lights
}

#used to request values from lowcar (non-polled)
HEADER_COMMAND_MAPPINGS = {

}

arduinos = {
    arduino_1.get_identifier(): arduino_1, 
    arduino_2.get_identifier(): arduino_2,
}

################################################