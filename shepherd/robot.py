from datetime import datetime
import random
import math
from utils import *
from code import *

# TODO: rewrite this whole class for evergreen


class Robot:

    def __init__(self, name, number, custom_ip=None):
        self.name: str = name
        self.number: int = number
        self.custom_ip = custom_ip or f"192.168.128.{number + 100}"
        self.coding_challenge = [False] * 8
        self.starting_position = None
    
    def init_times(self):
        self.start_time: datetime = None
        self.end_time = None
        self.stamp_time = 0
        self.penalty = 0
        self.stamp_time = 0

    def set_elapsed_time(self, new_time):
        if self.start_time:
            self.end_time = self.start_time + new_time

    def elapsed_time(self):
        if self.end_time is not None and self.start_time is not None:
            return self.end_time - self.start_time
        return None    

    def total_time(self):
        elapsed = self.elapsed_time()
        if elapsed is None:
            return None
        return elapsed + self.stamp_time + self.penalty

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
        return f"Robot({self.number} {self.name})"
