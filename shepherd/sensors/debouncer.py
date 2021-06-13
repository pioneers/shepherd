import sys
sys.path.insert(1, '../')
from typing import Union
from sensors import Parameter
class Debouncer:
    def __init__(self):
        self.previous_parameter_values = {}

    def debounce(self, value: Union[int, float, bool], param: Parameter):
        """
        This method performs debouncing by TODO
        updates state, be careful
        If there is no debouncing, it returns the value.
        """
        if param.debounce_threshold is not None:
            # Begin Debouncing
            if param not in self.previous_parameter_values:
                self.previous_parameter_values[param] = []
            prev_values = self.previous_parameter_values[param]
            prev_values.append(value)
            if len(prev_values) > param.debounce_threshold:
                prev_values.pop(0)
            # ex: if 70% of samples greater than some value
            for value in set(prev_values):
                if len([v for v in prev_values if v == value]) / param.debounce_threshold > param.debounce_sensitivity:
                    return value
            return None

        return value