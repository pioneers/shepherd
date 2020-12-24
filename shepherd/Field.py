import random

class Field:

    def __init__(self):
        self.buttons_illuminated = [False] * 6
        self.correct_button = random.randint(0, 5)

    def illuminate_buttons(self, robot):
        passed = robot.pass_coding_challenges(n=5)
        to_illuminate = random.sample(range(len(self.buttons_illuminated)), len(self.buttons_illuminated) - passed)
        for btn in to_illuminate:
            self.buttons_illuminated[btn] = True
            # TODO: illuminate btn

    def press_button_and_check(self, button):
        self.buttons_illuminated[button] = False
        return self.is_correct_button(button)

    def is_correct_button(self, button):
        return button == self.correct_button