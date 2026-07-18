"""
robot.py — Plain data holder for one competing team's robot.

Four Robot instances exist (2 per Alliance, see shepherd.py's ALLIANCES).
Holds the team name/number and per-match state; info_dict() is the shape
sent to the UI in TEAMS_INFO messages. The robot's network connection is
NOT here — that's runtimeclient.py, keyed by the same INDICES.
"""
from datetime import datetime
import random
import math
from utils import *

# TODO: rewrite this whole class for evergreen


class Robot:

    def __init__(self, name: str, number: int):
        self.name: str = name
        self.number: int = number
        self.coding_challenge = []
        self.starting_position = None

    def reset(self):
        self.coding_challenge = []
        self.starting_position = None

    def set_from_dict(self, dic: dict):
        self.name = dic["team_name"]
        self.number = dic["team_num"]
        self.starting_position = dic.get("starting_position", self.starting_position)

    def info_dict(self, robot_ip):
        return {
            "team_name": self.name,
            "team_num": self.number,
            "starting_position": self.starting_position,
            "robot_ip": robot_ip
        }

    def __str__(self):
        return f"Robot({self.number} {self.name})"
