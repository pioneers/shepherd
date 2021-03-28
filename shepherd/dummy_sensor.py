import LCM
from Utils import *
import time

# Arduino 1 Write Tests
"""
for i in range(7):
    args = {"id" : i}
    LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, args)
    time.sleep(0.5)
    LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, args)
"""

# Arduino 2 Write Tests
"""
LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_FIRE_LIGHT)
time.sleep(2)
LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_FIRE_LIGHT)
"""

# Arduino 3 Write Tests

LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "green"})
# time.sleep(2)
# LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "red"})
# time.sleep(2)
# LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_TRAFFIC_LIGHT)


# Arduino 4 Write Tests
"""
LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LASERS)
time.sleep(2)
LCM.lcm_send(LCM_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LASERS)
"""
