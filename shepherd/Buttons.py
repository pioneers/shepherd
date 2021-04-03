import random
from Utils import *
from LCM import *

class Buttons:

    NUM_BUTTONS = 7

    def __init__(self):
        self.buttons_illuminated = [True] * self.NUM_BUTTONS
        self.illuminate_buttons()
        self.correct_button = random.randint(0, self.NUM_BUTTONS - 1)
        self.illuminated = self.NUM_BUTTONS
        # pick the indices of 7 challenges
        self.challenges = random.sample(range(8), self.NUM_BUTTONS)
        print(self.correct_button)

    def randomize_correct_button(self):
        self.correct_button = random.choice(
            [i for i in range(self.NUM_BUTTONS) if self.buttons_illuminated[i]])

    def illuminate_buttons(self):
        """
        Turns on button i if self.buttons_illuminated[i] is True.
        """
        for i in range(self.NUM_BUTTONS):
            if self.buttons_illuminated[i]:
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, {
                         "id": i})

    def press_button_and_check(self, button_id, robot):
        # if this is the correct button and the challenge was solved
        if self.is_correct_button(button_id) and robot.coding_challenge[self.challenges[button_id]]:
            for i in range(self.NUM_BUTTONS):
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {
                         "id": i})
            self.illuminated = 0
            self.buttons_illuminated = [False] * self.NUM_BUTTONS
            return True
        # if this is not the correct button and the challenge was solved
        if self.buttons_illuminated[button_id] and robot.coding_challenge[self.challenges[button_id]]:
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
        new_buttons.challenges = self.challenges
        return new_buttons
