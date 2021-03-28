import LCM
from Utils import *
import time
args = {"id" : 0}
LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, args)
