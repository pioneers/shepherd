import random
import Utils

class Buttons:

    def __init__(self):
        self.NUM_BUTTONS = 7
        self.buttons_illuminated = [True] * self.NUM_BUTTONS
        self.correct_button = random.randint(0, self.NUM_BUTTONS - 1)
        self.illuminated = self.NUM_BUTTONS
        # pick the indices of 7 challenges
        self.challenges = random.sample(range(8), self.NUM_BUTTONS)

    def randomize_correct_button(self):
        self.correct_button = random.choice(
            [i for i in range(len(self.NUM_BUTTONS)) if self.buttons_illuminated[i]])

    def illuminate_buttons(self):
        for i in range(self.NUM_BUTTONS):
            if self.buttons_illuminated[i]:
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, {num: button_to_id(i)})

    def press_button_and_check(self, button_id, robot):
        button = self.id_to_button(button_id)
        if self.is_correct_button(button) and robot.coding_challenge[self.challenges[button]]: # if this is the correct button and the challenge was solved
            for i in range(self.NUM_BUTTONS):
                lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {num: button_to_id(i)})
            self.illuminated = 0
            self.buttons_illuminated = [False] * self.NUM_BUTTONS
            return True
        if self.buttons_illuminated[button] and robot.coding_challenge[self.challenges[button]]: # if this is not the correct button and the challenge was solved
            self.illuminated -= 1
            self.buttons_illuminated[button] = False
            lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, {num: button_id})
        return False

    def is_correct_button(self, button):
        return button == self.correct_button

    def button_to_id(self, button):
        return button #TODO
    
    def id_to_button(self, id):
        return id #TODO

    def copy(self):
        new_buttons = Buttons()
        new_buttons.buttons_illuminated = self.buttons_illuminated
        new_buttons.correct_button = self.correct_button
        new_buttons.illuminated = self.illuminated
        new_buttons.challenges = self.challenges
        return new_buttons
