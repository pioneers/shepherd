"""
A process that is the interface between LCM and shared memory.
It parses device commands from LCM and writes it to shared memory.
It reads device data from shared memory and publishes it to LCM if necessary.
- Ex: Provide the device uid and param index of a button
-     This will write to LCM if the button has been pressed.
"""

import threading
# import shm_api
import sys
sys.path.insert(1, '../')
import Sensors

#LCM -> TURN_ON_LIGHT, {light: 8}
#LCM -> SET_TRAFFIC_LIGHT, {color: "green"}

# START_BUTTON_PRESSED {} -> LCM

# figure out three things: 1) which device talking to, 2) which param of device to modify 3) value

# TURN_ON_LIGHT, {light: 8, brightness: 10}

#arduino 1: lights [1,2,3,6,7]
#arduino 2: lights [4,5,8], traffic_light

############################# NON-EVERGREEN FUNCTIONS #############################

# TODO: Shepherd please implement these as well as another TODO below

"""
A dictionary containing which parameters to watch out for:
Ex: buttons
    {
        {dev_id}_{dev_type} : ["param_name", "param_name_2"]
    }
"""
PARAMS_TO_READ = {

}

def read_lcm():
    """
    Reads an LCM message that is a command to one or more Lowcar devices
    Returns the LCM message.
    """
    pass

def parse_LCM(lcm):
    """
    Parses an LCM message into a LowcarMessage object
    """
    pass

def create_LCM(lowcar_message):
    """
    Create an LCM message based of a LowcarMessage object
    """
    pass

def should_send_LCM(lowcar_message):
    """
    Returns whether a LowcarMessage is worth sending an LCM message about to Shepherd
    Ex: LowcarMessage has "button_a" pressed -- return True
        LowcarMessage has "button_a" not pressed -- return False
    This acts as a "filter". We don't want to spam LCM messages about useless information.
    """
    pass

############################# START OF EVERGREEN FUNCTIONS #############################

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
                params[i] is a dictinary of parameters for device wat dev_ids[i]
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
        return self.dev_uids

    def get_params(self):
        return self.params

    def publish_LCM(self):
        """
        Converts a LowcarMessage to an LCM message and publishes it.
        Arguments:
            lowcar_message: A LowcarMessage object that should be sent over LCM
        Returns:
            None
        """
        # TODO: Shepherd please advise lol
        pass

def place_device_command(lowcar_message):
    """
    Reads a Lowcar command and writes it to shared memory.
    Arguments:
        lowcar_message: An LowcarMessage that contains a command for lowcar
    Returns:
        None
    """
    # Parse the LCM command
    all_dev_ids = lowcar_message.get_dev_ids()
    all_params = lowcar_message.get_params()

    for i in range(len(dev_ids)):
        dev_id = dev_ids[i]
        params = all_params[i]
        for (name, val) in params.items():
            set_value(dev_id, name, val)

def read_device_data(dev_id, param_name):
    """
    Reads the current device data from shared memory.
    Arguments:
        dev_id: String of form {dev_type}_{dev_uid}
        param_name: String corresponding to the name of the param type
    Returns:
        LowcarMessage: holds the param value
    """
    dev_params = get_value(dev_id, param_name)  # returns param value corresponding to param_name
    return LowcarMessage([dev_id], [{param_name: dev_param}])

def thread_device_commander():
    """
    Thread function
    Reads commands from LCM and writes it to shared memory.
    """
    while (True):
        lcm_message = read_lcm()
        lowcar_message = parse_LCM(lcm_message)
        place_device_command(lowcar_message)

def thread_device_sentinel(params_to_read):
    """
    Thread function
    Polls shared memory for specified parameters. If they change, write to LCM.
    Ex: Button is pressed
    Arguments:
        A dictionary containing which parameters to watch out for:
            {
                {dev_id}_{dev_type} : ["param_name", "param_name_2"]
            }
    Returns:
        None
    """
    while (True):
        for device, params in params_to_read:
            dev_data = read_device_data(device, params)
            if should_send_LCM(dev_data):
                dev_data.publish_LCM()

def main():
    try:
        device_thread = threading.Thread(target=thread_device_commander)
        device_sentinel_thread = threading.Thread(target=thread_device_sentinel, args=(PARAMS_TO_READ))
    except:
        print("Couldn't start device_commander() thread")

if __name__ == "__main__":
    main()
