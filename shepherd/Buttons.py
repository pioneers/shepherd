import random

class Buttons:

    def __init__(self):
        self.NUM_BUTTONS = 7
        self.buttons_illuminated = [True] * self.NUM_BUTTONS
        self.correct_button = random.randint(0, self.NUM_BUTTONS - 1)
        self.illuminated = self.NUM_BUTTONS

    def set_num_buttons(self):
        #TODO: idk
        pass

    def randomize_buttons(self):
        random.shuffle(self.buttons_illuminated)
        self.correct_button = \
            random.choice([a for a in range(self.NUM_BUTTONS) if self.buttons_illuminated[a]])

    def illuminate_buttons(self, robot):
        self.buttons_illuminated = [True] * self.NUM_BUTTONS 
        challenges = random.sample(range(len(robot.coding_challenge)), 5) # pick the indices of 5 challenges
        for c in range(len(challenges)):
            self.buttons_illuminated[c] = not robot.coding_challenge[challenges[c]]
        self.illuminated = sum(self.buttons_illuminated)

    def press_button_and_check(self, button):
        self.buttons_illuminated[button] = False
        self.illuminated -= 1
        return self.is_correct_button(button)

    def is_correct_button(self, button):
        return button == self.correct_button