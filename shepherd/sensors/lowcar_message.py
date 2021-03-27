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
                params[i] is a dictionary of parameters for device wat dev_ids[i]
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