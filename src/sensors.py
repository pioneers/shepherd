"""
here thar be dragons, venture at your own peril

The main purpose of this file is to talk to Arduinos. Arduinos/devices have lots
of physical things attached to them, but we can abstract those away as input and
output pins. A single physical thing may correspond to multiple pins; for
example, a traffic light uses 2 output pins. A linebreak sensor will typically
involve 2-6 pins:
 - a digital output pin for the laser
 - a pulse input pin for the color sensor
 - optionally 4 digital output pins for the config pins, but those could be
   hardwired to vcc and ground.

Ideally, the only code that should have to be modified is the Python
configuration (what pin objects and which arduinos they're on), and the MY_UUID
constant in the arduino code.

The general design is that Python will scan availible files until it finds
availible serial ports, and then attempt to connect to those serial ports and
start a polling loop.

Some notes about the general design of the polling loop:
 - the arduinos we use only have one serial port, so that serial port needs to
   handle both input and output. This unfortunately necessitates polling, as
   opposed to a more efficient event-based model.
 - since we're polling anyway, there's no point in limiting the frequency of
   data sent. This leads to a very simple design: on each poll, data from every
   output pin is sent to the arduino, and data from every input pin is received
   from the arduino. All processing (such as debouncing) is handled by Python.
 - The handshake protocol goes roughly like this:
    - arduino -> host: 4-byte magic, 4 byte UUID. Magic is to make sure the
      right version of code is flashed to the arduino; if arduino code is
      updated, it's a good idea to update magic as well.
    - host -> arduino: 1-byte number of pins, 2N byte config. This "sets up" the
      arduino with input and output pins. From here on, let X be the number of
      input pins, and let Y be the number of output pins. Note that X+Y=N
    - arduino -> host: 1-byte number of pins, 1-byte checksum. This provides the
      arduino an opportunity to complain if anything goes wrong (such as too
      many pins specified, or an unrecognized pinmode)
 - once the handshake is completed, the main loop can start. Note that the
   pacing of the main loop is nominally set by Python (which sleeps in any extra
   time, as set by POLL_DELAY_MS), but will match the slower of the two sides
   since they wait for each other. The protocol goes roughly like this:
    - host -> arduino: 1+Y bytes. First byte is a dummy, mainly there in case Y
      is 0 (it's important for both sides to wait for each other). Each of the Y
      bytes corresponds to the value of an output pin.
    - arduino -> host: 1+X bytes. First byte is a dummy, mainly in case X is 0.
      This dummy byte could be also used as a poor man's print in dire
      situations, but hopefully it's never needed for that.
 - since we're dealing with physical hardware, there is a (very small) chance
   for bits to get corrupted. The handshake has a checksum to deal with that;
   the polling loop doesn't really care, since all information is repeated every
   time anyway. For digital values, there's a slight migitation in that a whole
   byte is used, so corrupted digital values will likely just get ignored.
"""

import termios
import time
import threading
import os
from enum import Enum

HANDSHAKE_MAGIC = 2734451328 # 4 byte random used to identify PIE devices
BAUDRATE = termios.B9600     # serial port communication speed

# types of peripherals:
# - digital input pin: (i.e. button)
# - pulse input pin (color sensor)
# - digital output pin (i.e. light)
# - analog output pin (idk but it's here)

class PinMode(Enum):
    DIGITAL_IN = 0
    PULSE_IN = 1
    DIGITAL_OUT = 2
    ANALOG_OUT = 3

# in case of bit corruption, these values reasonably different
class DigitalValue(Enum):
    HIGH = 0xC3
    LOW  = 0x34
    NULL = 0x0F


class Arduino:
    def __init__(self, uuid: int, onloop=lambda:None, poll_delay_ms=10):
        self.uuid = uuid
        self.lock = threading.Lock() # protects output pin values
        self.pins = []
        self.onloop = onloop # function that is called before every poll
        self.poll_delay_ms = poll_delay_ms

    def get_pin_counts(self):
        num_in = 0
        num_out = 0
        for pin in self.pins:
            if pin.pin_mode in [PinMode.DIGITAL_IN, PinMode.PULSE_IN]:
                num_in += 1
            elif pin.pin_mode in [PinMode.DIGITAL_OUT, PinMode.ANALOG_OUT]:
                num_out += 1
        assert num_in + num_out == len(self.pins), "pins must be input or output"
        return (num_in, num_out)

    def get_output_message(self, expected_length):
        msg = b'\x42' # first byte is a dummy byte
        with self.lock:
            for pin in self.pins:
                if pin.pin_mode in (PinMode.DIGITAL_OUT, PinMode.ANALOG_OUT):
                    msg += pin.state.to_bytes(1, "little")
        assert len(msg) == expected_length
        return msg

    def process_input_message(self, msg):
        idx = 1 # first byte is a dummy byte
        for pin in self.pins:
            if pin.pin_mode in (PinMode.DIGITAL_IN, PinMode.PULSE_IN):
                pin.update(msg[idx])
                idx += 1
        assert idx == len(msg)

class InputPin:
    def __init__(self, arduino: Arduino, pin: int, pin_mode:PinMode,
                 state_switch_fn, num_collect=8, thresh=0.99):
        self.arduino = arduino
        self.pin = pin
        self.pin_mode = pin_mode
        self.state_switch_fn = state_switch_fn
        self.num_collect = num_collect
        self.thresh = thresh
        self.last_value = None
        self.memory = [None] * num_collect
        self.index = 0
        with self.arduino.lock:
            self.arduino.pins.append(self)

    def update(self, value: int):
        self.memory[self.index] = value
        self.index = (self.index + 1) % self.num_collect
        if self.last_value != value and self.memory.count(value) >= self.thresh * self.num_collect:
            if self.last_value is not None:
                self.state_switch_fn(value)
            self.last_value = value

class OutputPin:
    def __init__(self, arduino: Arduino, pin: int, pin_mode:PinMode, initial_value: int):
        self.arduino = arduino
        self.pin = pin
        self.pin_mode = pin_mode
        self.state = initial_value
        with self.arduino.lock:
            self.arduino.pins.append(self)

    def set_state(self, value: int):
        assert isinstance(value, int) and 0 <= value <= 255
        with self.arduino.lock:
            self.state = value


def _serialport_init(serialport: str):
    f = open(serialport, "rb+", buffering=0)
    # https://www.man7.org/linux/man-pages/man3/termios.3.html
    # https://www.cmrr.umn.edu/~strupp/serial.html
    toptions = termios.tcgetattr(f)
    print(f"Old toptions for {serialport}: {toptions[:6]}")
    C_IFLAG, C_OFLAG, C_CFLAG, C_LFLAG, C_ISPEED, C_OSPEED, C_CC = (0,1,2,3,4,5,6)
    # set baud rate
    toptions[C_ISPEED] = termios.B9600
    toptions[C_OSPEED] = termios.B9600
    # set serialport config to 8-N-1, which is default for Arduino Serial.begin()
    toptions[C_CFLAG] &= ~termios.PARENB # disable parity bit
    toptions[C_CFLAG] &= ~termios.CSTOPB # set only 1 stop bit
    toptions[C_CFLAG] &= ~termios.CSIZE  # reset character size
    toptions[C_CFLAG] |= termios.CS8     # set character size to 8
    # make raw, which disables special processing of input and output bytes
    # see https://linux.die.net/man/3/cfsetspeed
    # random C flags:
    toptions[C_CFLAG] &= ~termios.CRTSCTS # disable hardware flow control
    toptions[C_CFLAG] |= termios.CREAD | termios.CLOCAL # turn on READ & ignore ctrl lines
    toptions[C_IFLAG] &= ~(termios.IXON | termios.IXOFF | termios.IXANY) # turn off s/w flow ctrl
    # cfmakeraw flags
    toptions[C_IFLAG] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP
                         | termios.INLCR | termios.IGNCR | termios.ICRNL) # cfmakeraw
    toptions[C_OFLAG] &= ~(termios.OPOST) # cfmakeraw
    toptions[C_LFLAG] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON | termios.ISIG
                         | termios.IEXTEN) # cfmakeraw
    # flags that pyserial also unsets (basically, want C_OFLAG and C_LFLAG to be 0)
    toptions[C_OFLAG] &= ~(termios.ONLCR) # map ML to CR-NL on output
    toptions[C_LFLAG] &= ~(termios.ECHOE | termios.ECHOK | termios.ECHOCTL | termios.ECHOKE) # :(

    # set options for read
    TIMEOUT = 1000
    toptions[C_CC][termios.VMIN] = 0
    toptions[C_CC][termios.VTIME] = TIMEOUT // 100 # deciseconds until timeout

    termios.tcsetattr(f, termios.TCSANOW, toptions)
    termios.tcsetattr(f, termios.TCSAFLUSH, toptions)
    print(f"New toptions for {serialport}: {termios.tcgetattr(f)[:6]}")
    return f

class ReadingSerialException(Exception):
    pass

def _read_msg(f, num_bytes):
    '''Read an n-byte message from the file object'''
    buf = b''
    c = 0
    while len(buf) < num_bytes:
        buf += f.read(num_bytes - len(buf))
        c += 1
        if c >= 100:
            raise ReadingSerialException("too many loops")
    if len(buf) > num_bytes:
        print("Uh oh bad thing happened when reading message")
    return buf[0:num_bytes]


def _sleep_until(target_time):
    cur = time.time()
    if cur < target_time:
        time.sleep(target_time - cur)
    return time.time()

def _start_read_loop(f, arduinos):
    '''
    Given an opened serial port (f), attempt to handshake with it.
    On a successful handshake, poll it for the corresponding arduino's
    input and output pins.
    '''

    print(f"Starting read loop for {f.name}")

    # first part of handshake: arduino sends 4 byte magic number,
    # then its 4 bytes UUID
    initial_message = _read_msg(f, 8)
    if int.from_bytes(initial_message[:4], 'little') != HANDSHAKE_MAGIC:
        print(f"WARNING: Failed handshake - please unplug device at {f.name} immediately")
        return
    uuid = int.from_bytes(initial_message[4:8], 'little')
    matching = [ard for ard in arduinos if ard.uuid == uuid]
    if len(matching) != 1:
        print(f"WARNING: Device at {f.name} has uuid {uuid},"
                +" but could not find arduino with that uuid")
        return
    print(f"Arduino {uuid} detected at {f.name}")

    # second part of handshake: host sends 1 byte number of pins used,
    # then 2 bytes for each pin (1 byte pin number, 1 byte pin type)
    arduino = matching[0]
    input_pins, output_pins = arduino.get_pin_counts()
    f.write(len(arduino.pins).to_bytes(1, "little"))
    checksum = 0
    for pin in arduino.pins:
        msg = pin.pin.to_bytes(1, "little") + pin.pin_mode.value.to_bytes(1, "little")
        checksum = checksum ^ msg[0] ^ msg[1]
        f.write(msg)

    # third part of handshake: receive number of pins back
    confirmation = _read_msg(f, 2)
    if confirmation[0] != len(arduino.pins) or confirmation[1] != checksum:
        print(f"WARNING: Device at {f.name} did not complete handshake. "
            + f"Expected {len(arduino.pins)}, {checksum} "
            + f"but received {confirmation[0]} {confirmation[1]}")
        return
    print(f"Handshake completed for Arduino {uuid}")


    # poll in a loop
    # polling follows a request-response model: first, host sends
    # an (1+y)-byte message, where y is the number of output pins
    # then, arduino responds with a (1+x)-byte message, where x is the number of
    # input pins. Each message begins with a dummy byte.
    # pins are in same order as arduin.pins array
    current_time = time.time()
    while True:
        arduino.onloop()
        f.write(arduino.get_output_message(1 + output_pins))
        arduino.process_input_message(_read_msg(f, 1 + input_pins))
        current_time = _sleep_until(current_time + arduino.poll_delay_ms / 1000)


def _attempt_read_loop(filename, arduinos):
    while True:
        if os.path.exists(filename):
            try:
                f = _serialport_init(filename)
                _start_read_loop(f, arduinos)
            except PermissionError:
                print(f"PermissionError on {filename}")
            except (OSError, ReadingSerialException):
                print(f"Disconnected from {filename}")
                f.close()
        time.sleep(2)

def start_device_handlers(potential_filenames, arduinos):
    '''
    Given a list of potential filenames for serial ports, attempt to connect
    to them if they appear. One thread is started for each potential filename.
    Handles automatically connecting/disconnecting.
    '''
    for filename in potential_filenames:
        threading.Thread(target=_attempt_read_loop, args=(filename, arduinos), daemon=True).start()
