import random
from Utils import *


class Robot:

    def __init__(self, name, number, custom_ip=None):
        self.name = name
        self.number = number
        self.custom_ip = custom_ip or f"192.168.128.{number + 100}"
        self.connection = False
        print(self.custom_ip)

        self.coding_challenge = [False] * 10  # TODO: change
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.penalty = 0

    def calculate_time(self):
        if self.end_time is not None and self.start_time is not None:
            self.elapsed_time = (
                self.end_time - self.start_time).total_seconds()

    def reset(self):
        self.connection = False

    def run_coding_challenges(self):
        # TODO
        pass

    def pass_all_coding_challenges(self):
        return all(self.coding_challenge)

    def pass_coding_challenges(self, n=1):
        """
        TODO: Does this need to take a tier? yes
        runs n random coding challenges
        returns how many were passed
        """
        to_sample = random.sample(range(len(self.coding_challenge)), n)
        return sum([self.coding_challenge[i] for i in to_sample])

    def __str__(self):
        return f"{self.number} {self.name}"
