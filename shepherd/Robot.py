from datetime import datetime
import random
from Utils import *


class Robot:

    def __init__(self, name, number, custom_ip=None):
        self.name: str = name
        self.number: int = number
        self.custom_ip = custom_ip or f"192.168.128.{number + 100}"
        self.connection = False
        print(self.custom_ip)

        self.coding_challenge = [False] * 8
        self.start_time: datetime = None
        self.end_time = None
        self.elapsed_time = None
        self.stamp_time = 0
        self.penalty = 0
        self.stamp_time = 0

    def calculate_time(self):
        if self.end_time is not None and self.start_time is not None:
            self.elapsed_time = (
                self.end_time - self.start_time).total_seconds()

    def total_time(self):
        return self.elapsed_time + self.stamp_time + self.penalty

    def reset(self):
        self.connection = False

    def run_coding_challenges(self):
        # TODO
        pass

    def pass_all_coding_challenges(self):
        return all(self.coding_challenge)

    def pass_coding_challenges(self, n=1, tier=None):
        """
        runs n random coding challenges of tier {tier}
        returns how many were passed
        """
        if tier is None:
            valid = self.coding_challenge
        elif tier == 1:
            valid = self.coding_challenge[:4]
        else:
            valid = self.coding_challenge[4:]
        to_sample = random.sample(range(len(valid)), n)
        return sum([valid[i] for i in to_sample])

    def __str__(self):
        return f"{self.number} {self.name}"
