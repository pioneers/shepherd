import random
from Utils import *

class Robot:

    def __init__(self, name, number, alliance, custom_ip=None):
        self.name = name
        self.number = number
        self.custom_ip = custom_ip
        self.connection = False
        self.alliance = alliance

        self.coding_challenge = []
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.penalty = 0

    def calculate_time(self):
        if self.end_time is not None and self.start_time is not None:
            self.elapsed_time = self.end_time - self.start_time

    def reset(self):
        self.connection = False

    def pass_all_coding_challenges(self):
        return all(self.coding_challenge)

    def pass_coding_challenges(self, n=1):
        """
        TODO: Does this need to take a tier? yes
        runs n random coding challenges
        returns how many were passed
        """
        to_sample = random.choice(range(len(self.coding_challenge), n))
        return sum([self.coding_challenge[i] for i in to_sample])

    def __str__(self):
        return f"{self.number} {self.name}"