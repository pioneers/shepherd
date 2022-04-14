#YDL -> TURN_ON_LIGHT, {"id": 4}
#YDL -> SET_TRAFFIC_LIGHT, {"id": ???, color : "green"}

# START_BUTTON_PRESSED {} -> YDL

# figure out three things: 1) which device talking to, 2) which param of device to modify 3) value

# TURN_ON_LIGHT, {light : 7}

#arduino 1: lights [0,1,2,5,6]
#arduino 2: lights [3,4,7], traffic_light

# Dev Handler should get something in the form
# device 8, parameter 1, value 1.0

"""
YDL Messages to Sensors.py should follow this format:

[HEADER, {args}]

args: {
    id : #
    variables : values
}

Details for each header will live in Utils.py
"""
from __future__ import annotations
from utils import SENSOR_HEADER, SHEPHERD_HEADER
import queue
import time

################################################
# Evergreen Methods
################################################

class LowcarMessage:
    """
    Representation of a packet of data from or command to a lowcar device
    Detailing which devices (by year, uid), parameters, and the parameters' values are affected
    """
    def __init__(self, dev_ids, params):
        """
        Arguments:
            dev_ids: A list of device ids strings of the format '{device_type}_{device_uid}'
            params: A list of dictionaries
                params[i] is a dictionary of parameters for device dev_ids[i]
                key: (str) parameter name
                value: (int/bool/float) the value that the parameter should be set to
        Ex: We want to write to device 0x123 ("Device A") and 0x456 ("Device B")
            Lets say we want to turn on an LED ("LED_X") on Device A
            Lets say we want to dim an LED ("LED_Y") on Device B to 20% brightness
            Let's say Devices A and B have device type 50
            dev_ids = ["50_123", "50_456"]
            params = [
                {
                    "LED_A": 1.0
                },
                {
                    "LED_B": 0.2
                }
            ]
        """
        self.dev_ids = dev_ids
        self.params = params

    def get_dev_ids(self):
        return self.dev_ids

    def get_params(self):
        return self.params
    
    def __repr__(self):
        return f"LowcarMessage(dev_ids={self.dev_ids}, params={self.params})"

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
            parameter.device = self
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
        return self.params.get(param)
    
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
             this corresponds to the "id" in the YDL header args: { id : 1, variables : values}
    - a parent device (arduino) that owns this sensor
    TODO: talk about debounce_threshold and debounce_sensitivity
    """
    def __init__(self, name: str, should_poll: bool, identifier=None, debounce_threshold=None, debounce_sensitivity=0.7,ydl_header=None):
        self.name = name
        self.should_poll = should_poll
        self.identifier = identifier
        self.__device = None
        self.debounce_threshold = debounce_threshold
        self.debounce_sensitivity = debounce_sensitivity
        self.ydl_header = ydl_header

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
    
    def is_state_change_significant(self, value, previous_value: float):
        raise Exception("override this function you sad little sheep")
    
    def ydl_message_from_state_change(self, value: float):
        # feel free to add previous_value as a param if needed
        raise Exception("override this function you sad little sheep")

    def __repr__(self):
        return f"Parameter({self.name}, {self.identifier})"

def parameter_from_header(header):
    """
    Gets the parameter (sensor) that a header corresponds to.
    """
    sensor_pool = HEADER_MAPPINGS[header[0]]
    args = header[1]
    for p in sensor_pool:
        if p.identifier is None or args.get("id", None) == p.identifier:
            return p
    raise Exception(f'no device found associated with YDL header {header}')

def translate_ydl_message(header):
    """
    This method will decode three import pieces of information:
    1) the arduino and device to talk to
    2) the parameter of device to modify
    3) the value to modify it to
    """
    parameter: Parameter = parameter_from_header(header)
    device = f'{parameter.device.type}_{parameter.device.uuid}'
    value = parameter.value_from_header(header)
    message = LowcarMessage([device], [{parameter.name:value}])
    return message
    
previous_debounced_value = {} # TODO: move this.

################################################
# Game Specific Variables
################################################



# This is what sensors looked like in Spring 2021
# Feel free to take inspiration from this code
# or burn it with fire

# Look in "sensors overview/underview" on the wiki for more info
# also look at comments in Parameter class and Device class above

class Light(Parameter):
    def value_from_header(self, header):
        if (header[0] == SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name
            or header[0] == SENSOR_HEADER.TURN_ON_MIDLINE.name
            or header[0] == SENSOR_HEADER.TURN_ON_LASERS.name):
            return True
        if (header[0] == SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name
            or header[0]  == SENSOR_HEADER.TURN_OFF_MIDLINE.name
            or header[0]  == SENSOR_HEADER.TURN_OFF_LASERS.name):
            return False
        raise Exception(f"Attempting to get value of light, but header[0] is {header[0]}")

class DehydrationButton(Parameter):
    def is_state_change_significant(self, value: bool, previous_value: bool):
        return value == True and previous_value == False

    def ydl_message_from_state_change(self, value: float):
        # fire lever, traffic button
        args = {
            "button": self.identifier
        }
        return args
        # self.identifier is which button
"""

class GenericButton(Parameter):
    def is_state_change_significant(self, value: bool, previous_value: bool):
        return value == True and previous_value == False

    def ydl_message_from_state_change(self, value: float):
        # fire lever, traffic button, linebreak sensors
        args = {}
        return args

class TrafficLight(Parameter):
    # COLORS = {"red" : 0xFF0000, "green" : 0x00FF00, "yellow" : 0xFFFF00}

    def value_from_header(self, header):
        # this relationship is documented in shepherd_utils.c
        if header[0] == SENSOR_HEADER.TURN_OFF_TRAFFIC_LIGHT:
            return 0
        elif header[0] == SENSOR_HEADER.SET_TRAFFIC_LIGHT:
            color = header[1]["color"]
            if color == "red":
                return 1
            elif color == "green":
                return 2
            else:
                raise Exception("Traffic light can only be red or green.")
        raise Exception(f"Attempting to get value of traffic light but header[0] is {header[0]}")
"""

#linebreak_debounce_threshold = 10 # samples

# how fast are we polling? 100 Hz
"""
city_linebreak = GenericButton(name="city_linebreak", should_poll=True, identifier=0, ydl_header=SHEPHERD_HEADER.CITY_LINEBREAK, debounce_threshold=linebreak_debounce_threshold)
traffic_linebreak = GenericButton(name="traffic_linebreak", should_poll=True, identifier=1, ydl_header=SHEPHERD_HEADER.STOPLIGHT_CROSS, debounce_threshold=linebreak_debounce_threshold)
desert_linebreak = GenericButton(name="desert_linebreak", should_poll=True, identifier=2, ydl_header=SHEPHERD_HEADER.DESERT_ENTRY, debounce_threshold=linebreak_debounce_threshold)
dehydration_linebreak = GenericButton(name="dehydration_linebreak", should_poll=True, identifier=3, ydl_header=SHEPHERD_HEADER.DEHYDRATION_ENTRY, debounce_threshold=linebreak_debounce_threshold)
hypothermia_linebreak = GenericButton(name="hypothermia_linebreak", should_poll=True, identifier=4, ydl_header=SHEPHERD_HEADER.HYPOTHERMIA_ENTRY, debounce_threshold=linebreak_debounce_threshold)
airport_linebreak = GenericButton(name="airport_linebreak", should_poll=True, identifier=5, ydl_header=SHEPHERD_HEADER.FINAL_ENTRY, debounce_threshold=linebreak_debounce_threshold)

fire_lever = GenericButton(name="fire_lever", should_poll=True, ydl_header=SHEPHERD_HEADER.FIRE_LEVER)

traffic_button = GenericButton(name="traffic_button", should_poll=True, ydl_header=SHEPHERD_HEADER.STOPLIGHT_BUTTON_PRESS)
traffic_light = TrafficLight(name="traffic_light", should_poll=False)
"""


#num_dehydration_buttons = 7

#dehydration_buttons = [DehydrationButton(name=f"button{i}", should_poll=True, \
#    identifier=i, ydl_header=SHEPHERD_HEADER.BUTTON_PRESS.name) \
#        for i in range(num_dehydration_buttons)]
#lights = [Light(name=f"light{i}", should_poll=False, identifier=i) \
#    for i in range(num_dehydration_buttons)]
#fire_light = Light(name="fire_light", should_poll=False)

#lasers = Light(name="lasers", should_poll=False)


# button_0 = DehydrationButton(name="button0", should_poll=True, identifier=0, ydl_header=SHEPHERD_HEADER.BUTTON_PRESS.name)
# button_1 = DehydrationButton(name="button1", should_poll=True, identifier=1, ydl_header=SHEPHERD_HEADER.BUTTON_PRESS.name)
blight_0 = Light(name="light0", should_poll=False, identifier=0)
blight_1 = Light(name="light1", should_poll=False, identifier=1)
blight_2 = Light(name="light2", should_poll=False, identifier=2)
blight_3 = Light(name="light3", should_poll=False, identifier=3)
blight_4 = Light(name="light4", should_poll=False, identifier=4)
blight_5 = Light(name="light5", should_poll=False, identifier=5)


arduino_1 = Device(1, 1, [blight_0, blight_1, blight_4])
arduino_2 = Device(2, 2, [blight_2, blight_3, blight_5])
#arduino_2 = Device(2, 2, [desert_linebreak, dehydration_linebreak, hypothermia_linebreak, airport_linebreak, fire_lever, fire_light]) # fix NOW TODO
#arduino_3 = Device(3, 3, [city_linebreak, traffic_linebreak, traffic_button, traffic_light]) # fix
#arduino_4 = Device(4, 4, [lasers])


################################################
# Evergreen Variables (may still need to be updated)
################################################

HEADER_MAPPINGS = {
    SENSOR_HEADER.TURN_ON_BUTTON_LIGHT.name : [blight_0, blight_1, blight_2, blight_3, blight_4, blight_5],
    SENSOR_HEADER.TURN_OFF_BUTTON_LIGHT.name : [blight_0, blight_1, blight_2, blight_3, blight_4, blight_5],
    # SENSOR_HEADER.SET_TRAFFIC_LIGHT : [traffic_light],
    # SENSOR_HEADER.TURN_OFF_TRAFFIC_LIGHT : [traffic_light],
    # SENSOR_HEADER.TURN_ON_FIRE_LIGHT : [fire_light],
    # SENSOR_HEADER.TURN_OFF_FIRE_LIGHT : [fire_light],
    # SENSOR_HEADER.TURN_OFF_LASERS: [lasers],
    # SENSOR_HEADER.TURN_ON_LASERS: [lasers],
}

#used to request values from lowcar (non-polled)
HEADER_COMMAND_MAPPINGS = {

}

arduinos = {
    arduino_1.get_identifier(): arduino_1, 
    arduino_2.get_identifier(): arduino_2,
    # arduino_3.get_identifier(): arduino_3,
    # arduino_4.get_identifier(): arduino_4,
}

################################################
