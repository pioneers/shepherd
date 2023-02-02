from utils import *

class Alliance:
    """This is the Alliance class, which holds the state values used to track
       the scores and states of the alliances
    """

    def __init__(self, robot1, robot2):
        self.robot1 = robot1
        self.robot2 = robot2
        self.score = 0

    def set_score(self, new_score):
        self.score = new_score
        
    def reset(self):
        self.robot1.reset()
        self.robot2.reset()
        self.score = 0

    def __str__(self):
        return f"<alliance: robot1({self.robot1.__str__()}), robot2({self.robot2.__str__()}), score: {self.score}>"

