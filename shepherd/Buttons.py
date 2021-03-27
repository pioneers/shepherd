import random

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
            [i for i in range(self.NUM_BUTTONS) if self.buttons_illuminated[i]])

    def illuminate_buttons(self, robot):
        # TODO
        self.buttons_illuminated = [True] * self.NUM_BUTTONS
        # pick the indices of 5 challenges
        challenges = random.sample(range(len(robot.coding_challenge)), 5)
        for c in range(len(challenges)):
            self.buttons_illuminated[c] = not robot.coding_challenge[challenges[c]]
        self.illuminated = sum(self.buttons_illuminated)

    def press_button_and_check(self, button):
        if self.buttons_illuminated[button]:
            self.illuminated -= 1
        self.buttons_illuminated[button] = False
        return self.is_correct_button(button)

    def is_correct_button(self, button):
        return button == self.correct_button

    def copy(self):
        new_buttons = Buttons()
        new_buttons.buttons_illuminated = self.buttons_illuminated
        new_buttons.correct_button = self.correct_button
        new_buttons.illuminated = self.illuminated
        new_buttons.challenges = self.challenges
        return new_buttons
