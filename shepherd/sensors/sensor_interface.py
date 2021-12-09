"""
A process that is the interface between YDL and shared memory.
It parses device commands from YDL and writes it to shared memory.
It reads device data from shared memory and publishes it to YDL if necessary.
- Ex: Provide the device uid and param index of a button
-     This will write to YDL if the button has been pressed.
"""
import threading
import time
import queue
# import pyximport
# pyximport.install()
import shm_api
import sys
sys.path.insert(1, '../')
from debouncer import Debouncer
from ydl import (
    ydl_send,
    ydl_start_read
)
from typing import List, Union
from sensors_config import (
    arduinos,
    translate_ydl_message,
    HEADER_MAPPINGS,
    HEADER_COMMAND_MAPPINGS,
    Parameter,
    previous_debounced_value,
    LowcarMessage
)
from utils import (
    YDL_TARGETS,
)
#YDL -> TURN_ON_LIGHT, {light: 8}
#YDL -> SET_TRAFFIC_LIGHT, {color: "green"}

# START_BUTTON_PRESSED {} -> YDL

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
    arduino.get_identifier(): arduino.polling_parameters for arduino in arduinos.values()
}
print(f"PARAMS TO READ {PARAMS_TO_READ}")

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
    Reads commands from YDL and writes it to shared memory.
    """
    print("started commander thread")
    events = queue.Queue()
    ydl_start_read(YDL_TARGETS.SENSORS, events)
    while True:
        payload = events.get(True)
        print(payload)
        if payload[0] in HEADER_MAPPINGS:
            # TODO: remove this, after dealing with all exceptions properly
            try:
                lowcar_message = translate_ydl_message(payload)
                place_device_command(lowcar_message)
            except Exception as e:
                print(f"Exception occured while translating {payload} to a LowcarMessage or placing command: {e}.")
        elif payload[0] in HEADER_COMMAND_MAPPINGS:
            HEADER_COMMAND_MAPPINGS[payload[0]](payload[1])

def thread_device_sentinel(params_to_read):
    """
    Thread function
    Polls shared memory for specified parameters. If they change, write to YDL.
    Ex: Button is pressed
    Arguments:
        A dictionary containing which parameters to watch out for:
            {
                {dev_id}_{dev_type} : ["param_name", "param_name_2"]
            }
    Returns:
        None
    """
    print("started sentinel thread")
    debouncer = Debouncer()
    while (True):
        time.sleep(0.01)
        # iterate through all devices
        for device in params_to_read:
            params: List[Parameter] = params_to_read[device] # list of parameters
            dev_data: LowcarMessage = read_device_data(device, [param.name for param in params])

            if not (len(dev_data.dev_ids) == 1) or not (len(dev_data.params) == 1):
                raise Exception("LowcarMessage should only contain information about one device, because only one device is being queried.")
            arduino = arduinos[device]
            param_values = dev_data.params[0] # Dictionary: param_name -> value
            for param_name, value in param_values.items():
                param = arduino.get_param(param_name)
                # below logs are for testing buttons, slowly
                # print(f"{param_name}: {value}")
                # time.sleep(.2)
                value = debouncer.debounce(value, param)
                if value is None:
                    continue # unable to debounce anything meaningful

                if (param in previous_debounced_value and
                     param.is_state_change_significant(value, previous_debounced_value[param])):
                    args = param.ydl_message_from_state_change(value)
                    print(f"Sending YDL message with header {param.ydl_header} and args {args}")
                    ydl_send(YDL_TARGETS.SHEPHERD, param.ydl_header, args)

                previous_debounced_value[param] = value

def main():
    try:
        shm_api.dev_handler_connect()
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
