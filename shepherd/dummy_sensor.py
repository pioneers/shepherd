import LCM
from Utils import *
import time

for i in range(7):
    args = {"id" : i}
    LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, args)
    time.sleep(1)
    LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, args)
