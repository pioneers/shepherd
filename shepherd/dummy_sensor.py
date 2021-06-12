from ydl import ydl_send, ydl_start_read
from utils import *
import time

# Arduino 1 Write Tests
"""
for i in range(7):
    args = {"id" : i}
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LIGHT, args)
    time.sleep(0.5)
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LIGHT, args)
"""

# Arduino 2 Write Tests

"""
YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_FIRE_LIGHT)
time.sleep(2)
YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_FIRE_LIGHT)
"""

# Arduino 3 Write Tests

"""
for i in range(10):
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "green"})
    time.sleep(2)
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "red"})
    time.sleep(2)
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "green"})
    time.sleep(2)
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.SET_TRAFFIC_LIGHT, {"color": "red"})
    time.sleep(2)
    YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_TRAFFIC_LIGHT, {})
"""

# Arduino 4 Write Tests


YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_ON_LASERS)
#time.sleep(2)
# YDL.ydl_send(YDL_TARGETS.SENSORS, SENSOR_HEADER.TURN_OFF_LASERS)

