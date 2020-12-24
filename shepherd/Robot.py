import random
from Utils import *

class Robot:

    def __init__(self):
        self.state = STATE.SETUP
        self.coding_challenge = []
        self.penalty = 0

    def pass_all_coding_challenges(self):
        return all(self.coding_challenge)

    def pass_coding_challenges(self, n=1):
        """
        TODO: Does this need to take a tier?
        runs n random coding challenges
        returns how many were passed
        """
        to_sample = random.choice(range(len(self.coding_challenge), n))
        return sum([self.coding_challenge[i] for i in to_sample])