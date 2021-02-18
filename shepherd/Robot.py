from datetime import datetime
import random
import math
from Utils import *
from Code import *

class Robot:

    def __init__(self, name, number, custom_ip=None):
        self.name: str = name
        self.number: int = number
        self.custom_ip = custom_ip or f"192.168.128.{number + 100}"
        self.connection = False
        print(self.custom_ip)

        self.coding_challenge = [False] * 8
        self.init_times()
    
    def init_times(self):
        self.start_time: datetime = None
        self.end_time = None
        self.elapsed_time = None
        self.stamp_time = 0
        self.penalty = 0
        self.stamp_time = 0

    def calculate_time(self):
        if self.end_time is not None and self.start_time is not None:
            self.elapsed_time = self.end_time - self.start_time

    def total_time(self):
        if self.elapsed_time is None:
            return None
        return self.elapsed_time + self.stamp_time + self.penalty

    def start_time_millis(self):
        if self.start_time is None:
            return None
        return math.floor(self.start_time * 1000)

    def reset(self):
        self.init_times()
        self.connection = False

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
