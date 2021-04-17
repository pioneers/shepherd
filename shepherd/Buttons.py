import random
from Utils import SENSOR_HEADER, LCM_TARGETS
from LCM import lcm_send


class Buttons:

    NUM_BUTTONS = 7

    def __init__(self):
        self.buttons_illuminated = [True] * self.NUM_BUTTONS
        self.illuminated: int = self.NUM_BUTTONS
        self.correct_button = 0

    def illuminate_all(self):
        for i in range(self.NUM_BUTTONS):
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, {
                "id": i})

    def enter_mirage_wall(self, challenges):
        """
        Select 6 challenges, turn off buttons based on number solved
        """
        self.illuminated = max(1, self.illuminated -
                               sum([random.sample(challenges, 6)]))
        self._illuminate_buttons()

    def _illuminate_buttons(self):
        """
        Turn on self.illuminated number of buttons (random), and pick one to be correct
        """
        chosen = random.sample(range(self.NUM_BUTTONS), self.illuminated)
        self.correct_button = random.choice(chosen)
        self.buttons_illuminated = [i for i in range(
            self.NUM_BUTTONS) if (i in chosen)]
        for i in range(self.NUM_BUTTONS):
            if self.buttons_illuminated[i]:
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, {
                         "id": i})
            else:
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {
                         "id": i})

    def press_button_and_check(self, button_id):
        """
        If they press the correct button, then all buttons get turned off
        and the function returns True.
        If they press a different button, it gets turned off and the function
        returns False.
        """
        if self.is_correct_button(button_id):
            for i in range(self.NUM_BUTTONS):
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {
                         "id": i})
            self.illuminated = 0
            self.buttons_illuminated = [False] * self.NUM_BUTTONS
            return True
        if self.buttons_illuminated[button_id]:
            self.illuminated -= 1
            self.buttons_illuminated[button_id] = False
            lcm_send(LCM_TARGETS.SENSORS,
                     SENSOR_HEADER.TURN_OFF_LIGHT, {"id": button_id})
        return False

    def is_correct_button(self, button):
        return button == self.correct_button

    def copy(self):
        new_buttons = Buttons()
        new_buttons.buttons_illuminated = self.buttons_illuminated
        new_buttons.correct_button = self.correct_button
        new_buttons.illuminated = self.illuminated
        return new_buttons
