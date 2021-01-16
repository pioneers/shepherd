import random

class Buttons:

    # TODO: make a new field every match
    def __init__(self):
        self.NUM_BUTTONS = 6
        self.buttons_illuminated = [True] * self.NUM_BUTTONS
        self.correct_button = random.randint(0, 5)
        self.illuminated = self.NUM_BUTTONS
        # self.shuffled = random.shuffle(list(range(self.NUM_BUTTONS)))
        # self.correct_button = self.shuffled[0]

    def set_num_buttons():
        pass
    def illuminate_buttons(self, robot):
        passed = robot.pass_coding_challenges(n=5)
        for i in range(min(passed, len(self.shuffled) - 1)):
            self.buttons_illuminated[self.shuffled.pop()] = True

    def illuminate_buttons(self, robot):
        passed = robot.pass_coding_challenges(n=5)
        to_illuminate = random.sample([i for i in range(self.NUM_BUTTONS) if self.buttons_illuminated[i] or i == self.correct_button], max(1, self.illuminated - passed)) # TODO: this is wrong
        self.buttons_illuminated = [False] * 6
        for btn in to_illuminate:
            self.buttons_illuminated[btn] = True
            # TODO: illuminate btn


    def press_button_and_check(self, button):
        self.buttons_illuminated[button] = False
        return self.is_correct_button(button)

    def is_correct_button(self, button):
        return button == self.correct_button