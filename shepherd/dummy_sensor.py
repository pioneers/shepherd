import LCM
from Utils import *
import time

LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LASERS, {})
"""
time.sleep(2)
LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LASERS, {})

for i in range(7):
    args = {"id" : i}
    LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, args)
    time.sleep(0.5)
    LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, args)
    """
