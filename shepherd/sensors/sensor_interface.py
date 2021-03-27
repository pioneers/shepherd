"""
A process that is the interface between LCM and shared memory.
It parses device commands from LCM and writes it to shared memory.
It reads device data from shared memory and publishes it to LCM if necessary.
- Ex: Provide the device uid and param index of a button
-     This will write to LCM if the button has been pressed.
"""
import threading
import time
import queue
import pyximport
pyximport.install()
import shm_api
import sys
sys.path.insert(1, '../')
from LCM import (
    lcm_send,
    lcm_start_read
)
from Sensors import (
    arduino_1,
    arduino_2,
    arduinos,
    translate_lcm_message,
    HEADER_MAPPINGS,
    HEADER_COMMAND_MAPPINGS,
    Parameter,
    previous_parameter_values,
    LowcarMessage
)
from Utils import (
    LCM_TARGETS,
)
#LCM -> TURN_ON_LIGHT, {light: 8}
#LCM -> SET_TRAFFIC_LIGHT, {color: "green"}

# START_BUTTON_PRESSED {} -> LCM

# figure out three things: 1) which device talking to, 2) which param of device to modify 3) value

# TURN_ON_LIGHT, {light: 8, brightness: 10}

#arduino 1: lights [1,2,3,6,7]
#arduino 2: lights [4,5,8], traffic_light

############################# NON-EVERGREEN FUNCTIONS #############################


"""
A dictionary containing which parameters to watch out for:
Ex: buttons
    {
        {dev_id}_{dev_type} : ["param_name", "param_name_2"]
    }
"""

PARAMS_TO_READ = {
    arduino_1.get_identifier(): arduino_1.polling_parameters,
    arduino_2.get_identifier(): arduino_2.polling_parameters
}

############################# START OF EVERGREEN FUNCTIONS #############################

def place_device_command(lowcar_message):
    """
    Reads a Lowcar command and writes it to shared memory.
    Arguments:
        lowcar_message: An LowcarMessage that contains a command for lowcar
    Returns:
        None
    """
    all_dev_ids = lowcar_message.get_dev_ids()
    all_params = lowcar_message.get_params()
    print(f"lowcar message is {lowcar_message}")
    for i in range(len(all_dev_ids)):
        dev_id = all_dev_ids[i]
        params = all_params[i]

        for (name, val) in params.items():
            shm_api.set_value(dev_id, name, val)

def read_device_data(dev_id, param_names):
    """
    TODO: Update docs
    Reads the current device data from shared memory.
    Arguments:
        dev_id: String of form {dev_type}_{dev_uid}
        param_name: String corresponding to the name of the param type
    Returns:
        LowcarMessage: holds the param value
    """
    param_vals = {}
    for param_name in param_names:
        param_vals[param_name] = shm_api.get_value(dev_id, param_name)

    return LowcarMessage([dev_id], [param_vals])

def thread_device_commander():
    """
    Thread function
    Reads commands from LCM and writes it to shared memory.
    """
    print("started commander thread")
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
    print("started commander thread")
    while (True):
        for device in params_to_read:
            params = params_to_read[device]
            dev_data: LowcarMessage = read_device_data(device, params)
            # debounce it TODO
            if not (len(dev_data.dev_ids) == 1) or not (len(dev_data.params) == 1):
                raise Exception("LowcarMessage should only contain information about one device, because only one device is being queried.")
            arduino = arduinos[device]
            params = dev_data.params[0] # string[]
            for param_name, device in params:
                value = params[param_name]
                param: Parameter = arduino.get_param(param_name)
                prev_value = previous_parameter_values[param]
                if param.should_send_LCM(value, prev_value):
                    args = param.lcm_message_from_state_change(value)
                    lcm_send(LCM_TARGETS.SHEPHERD, param.lcm_header, args)
                # TODO: make debouncer so this will need to be more cool
                previous_parameter_values[param] = value

def main():
    try:
        device_thread = threading.Thread(target=thread_device_commander)
        device_sentinel_thread = threading.Thread(target=thread_device_sentinel, args=(PARAMS_TO_READ,))
        device_thread.start()
        device_sentinel_thread.start()
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Couldn't start device_commander() thread. Encountered exception: {e}")
        raise e

if __name__ == "__main__":
    main()
