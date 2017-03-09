import csv
import asyncio
import inspect
import os
import time

from runtimeUtil import *

class Actions:
  @staticmethod
  async def sleep(seconds):
    await asyncio.sleep(seconds)

class StudentAPI:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager

  def _getSMValue(self, key, *args):
    """Returns the value associated with key.
    """
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, Exception):
      raise message
    return message

  def _setSMValue(self, value, key, *args):
    """Sets the value associated with key.
    """
    #statemanager passes exception, then check to see if returned value is exception or not
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, Exception):
      raise message
    return message

class Gamepad(StudentAPI):
  buttons = {
    "button_a" : 0,
    "button_b" : 1,
    "button_x" : 2,
    "button_y" : 3,
    "l_bumper" : 4,
    "r_bumper" : 5,
    "l_trigger" : 6,
    "r_trigger" : 7,
    "button_back" : 8,
    "button_start" : 9,
    "l_stick" : 10,
    "r_stick" : 11,
    "dpad_up" : 12,
    "dpad_down" : 13,
    "dpad_left" : 14,
    "dpad_right" : 15,
    "button_xbox" : 16
  }
  joysticks = {
    "joystick_left_x" : 0,
    "joystick_left_y" : 1,
    "joystick_right_x" : 2,
    "joystick_right_y" : 3
  }

  def __init__(self, toManager, fromManager):
    super().__init__(toManager, fromManager)
    self._get_gamepad()

  def _get_gamepad(self):
    self.all_gamepads = self._getSMValue("gamepads")

  def get_value(self, name, gamepad_number=0):
    gamepad_dict = self.all_gamepads[gamepad_number]
    if name in self.joysticks:
      return gamepad_dict["axes"][self.joysticks[name]]
    elif name in self.buttons:
      return gamepad_dict["buttons"][self.buttons[name]]
    raise StudentAPIKeyError()

class Robot(StudentAPI):
  deviceName_to_writeParams = {
    "TeamFlag" : ["s1", "s2", "s3", "s4"],
    "ServoControl" : ["servo0", "servo1"],
    "YogiBear" : ["duty_cycle", "pid_pos_setpoint", "pid_pos_kp", "pid_pos_ki", "pid_pos_kd", "current_thresh", "enc_pos"],
  }
  deviceName_to_readParams = {
    "LimitSwitch" : ["switch0", "switch1", "switch2"],
    "LineFollower" : ["left", "center", "right"],
    "Potentiometer" : ["pot0", "pot1", "pot2"],
    "YogiBear" : ["duty_cycle", "enc_pos", "enc_vel"],
    "RFID" : ["id", "tag_detect"],
  }
  param_to_valid_values = {
    "servo0" : [(int,), 0, 180],
    "servo1" : [(int,), 0, 180],
    "duty_cycle" : [(float, int), -1, 1],
    "pid_pos_setpoint" :[(float, int), -float("inf"), float("inf")],
    "pid_pos_kp" : [(float, int), 0, float("inf")],
    "pid_pos_ki" : [(float, int), 0, float("inf")],
    "pid_pos_kd" : [(float, int), 0, float("inf")],
    "current_thresh" : [(float, int), 2, 10],
    "enc_pos" : [(float, int), 0, 0],
    "s1" : [(bool,)],
    "s2" : [(bool,)],
    "s3" : [(bool,)],
    "s4" : [(bool,)],
  }

  def __init__(self, toManager, fromManager):
    super().__init__(toManager, fromManager)
    self._createSensorMapping()
    self._coroutines_running = set()
    self._get_all_sensors()

  def _get_all_sensors(self):
    self.peripherals = self._getSMValue('hibike', 'devices')

  def get_value(self, device_name, param):
    uid = self._hibikeGetUID(device_name)
    self._check_read_params(uid, param)
    return self.peripherals[uid][0][param][0]

  def set_value(self, device_name, param, value):
    uid = self._hibikeGetUID(device_name)
    self._check_write_params(uid, param)
    self._check_value(param, value)
    self.toManager.put([HIBIKE_COMMANDS.WRITE, [uid, [(param, value)]]])

  def run(self, fn, *args, **kwargs):
    """
    Starts a "coroutine", i.e. a series of actions that proceed
    independently of the main loop of code.

    The first argument must be a function defined with 'async def'.

    The remaining arguments are then passed to that function before it is
    called.

    Multiple simultaneous coroutines that use the same robot actuators will
    lead to surprising behavior. To help guard against errors, calling
    `run` with a `fn` argument that is currently running is a no-op.
    """
    if self.is_running(fn):
      return

    self._coroutines_running.add(fn)

    future = fn(*args, **kwargs)

    async def wrapped_future():
      await future
      self._coroutines_running.remove(fn)

    asyncio.ensure_future(wrapped_future())

  def is_running(self, fn):
    if not inspect.isfunction(fn):
      raise StudentAPIValueError("First argument to Robot.run must be a function")
    elif not inspect.iscoroutinefunction(fn):
      raise StudentAPIValueError("First argument to Robot.run must be defined with `async def`, not `def`")

    return fn in self._coroutines_running

  def _check_write_params(self, uid, param):
    device_type = uid >> 72
    valid_params = self.deviceName_to_writeParams[SENSOR_TYPE[device_type]]
    if param not in valid_params:
      raise StudentAPITypeError("Invalid param passed in, valid parameters for this device are: " + "".join(valid_params))

  def _check_read_params(self, uid, param):
    device_type = uid >> 72
    valid_params = self.deviceName_to_readParams[SENSOR_TYPE[device_type]]
    if param not in valid_params:
      raise StudentAPITypeError("Invalid param passed in, valid parameters for this device are: " + "".join(valid_params))

  def _check_value(self, param, value):
    valid_values = self.param_to_valid_values[param]
    if not isinstance(value, valid_values[0]):
      raise StudentAPIValueError("Invalid value type passed in, valid types for this param are: " + valid_values[0][0].__name__)
    if valid_values[0][0] == bool:
      return
    elif valid_values[0][0] == float or valid_values[0][0] == int:
      if not (valid_values[1] <= value <= valid_values[2]):
        raise StudentAPIValueError("Invalid value passed in, valid values for this param are: " + str(valid_values[1]) + " to " + str(valid_values[2]))

  def _createSensorMapping(self, filename="namedPeripherals.csv"):
    with open(filename, "r") as f:
      sensorMappings = csv.reader(f)
      self.sensorMappings = {name: int(uid) for name, uid in sensorMappings}

  def createKey(self, key, *args):
    """ Creates a new key, or nested keys if more than 1 key is passed in.
        If any nested key does not exist, it will be created.
    """
    self.toManager.put([SM_COMMANDS.CREATE_KEY, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
      raise message

  def getTimestamp(self, key, *args):
    """Returns the value associated with key.
    """
    self.toManager.put([SM_COMMANDS.GET_TIME, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
      raise message
    return message

  # TODO: Only for testing. Remove in final version
  def _hibikeSubscribeDevice(self, uid, delay, params):
    """Uses direct uid to access hibike."""
    self.toManager.put([HIBIKE_COMMANDS.SUBSCRIBE, [uid, delay, params]])

  def _hibikeGetUID(self, name):
    try:
      #TODO: Implement sensor mappings, right now uid is the number (or string of number)
      return int(name)
      #return self.sensorMappings[name]
    except:
      raise StudentAPIKeyError()

  def emergencyStop(self):
    self.toManager.put([SM_COMMANDS.EMERGENCY_STOP, []])

  def _print(self, *args):
    print(*args)
    #TODO reimplement when dawn can handle higher hz communication
    #console_string = " ".join(str(arg) for arg in args)
    #self.toManager.put([SM_COMMANDS.SEND_CONSOLE, [console_string]])

  def hibikeWriteValue(self, uid, params):
    self.toManager.put([HIBIKE_COMMANDS.WRITE, [uid, params]])
