from datetime import datetime
import random
import math
from utils import *
from code import *

# TODO: rewrite this whole class for evergreen


class Robot:

    def __init__(self, name: str, number: int):
        self.name: str = name
        self.number: int = number
        self.coding_challenge = [False] * 8
        self.starting_position = None

    def reset(self):
        self.coding_challenge = [False] * 8
        self.starting_position = None

    def set_from_dict(self, dic: dict):
        self.name = dic["team_name"]
        self.number = dic["team_num"]
        self.starting_position = dic["starting_position"]

    def info_dict(self, robot_ip):
        return {
            "team_name": self.name, 
            "team_num": self.number, 
            "starting_position": self.starting_position, 
            "robot_ip": robot_ip
        }

    def __str__(self):
        return f"Robot({self.number} {self.name})"
