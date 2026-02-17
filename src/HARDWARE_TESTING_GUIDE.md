# Arduino Hardware Testing Guide

## System Architecture

Your Arduino communication system consists of three layers:

### 1. **Arduino Firmware** (`sensors.ino`)
- Runs on each Arduino board
- Each Arduino has a unique `MY_UUID` identifier
- Handles pin configuration and I/O operations
- Communicates via USB serial at 9600 baud

### 2. **Python Communication Library** (`sensors.py`)
- Provides high-level Python interface to Arduinos
- Handles serial communication and handshaking
- Implements polling loop for continuous data exchange
- Thread-safe pin control

### 3. **Application Layer** (`sensors_config.py`)
- Your specific hardware configuration
- Defines all physical pin connections
- Implements business logic and YDL integration

## How Communication Works

### Handshake Protocol
```
1. Arduino → PC: "Here I am! My UUID is X"
2. PC → Arduino: "Configure these pins like this"
3. Arduino → PC: "OK, I configured them. Here's a checksum"
```

### Continuous Polling Loop
```
PC → Arduino: [Output values for all output pins]
Arduino → PC: [Input values from all input pins]
(Repeats ~100 times per second)
```

### Pin Types

| Pin Mode | Purpose | Example Use |
|----------|---------|-------------|
| `DIGITAL_IN` | Read button presses | Buttons with debouncing |
| `PULSE_IN` | Read pulse sensors | Color sensors |
| `DIGITAL_OUT` | Control on/off devices | LEDs, relays |
| `ANALOG_OUT` | PWM control | Servo motors, LED brightness |

## Testing Your Arduino Hardware

### Step 1: Flash the Arduino

1. Open `sensors/sensors.ino` in Arduino IDE
2. Change `MY_UUID` to a unique number (1-255):
   ```cpp
   #define MY_UUID 1  // Change this!
   ```
3. Upload to your Arduino
4. Note which USB port it's connected to

### Step 2: Run Quick Connectivity Test

Use `quick_test.py` to verify basic connectivity:

```bash
# Edit quick_test.py: set TEST_UUID to match your Arduino
python3 quick_test.py
```

**What should happen:**
- Script connects to Arduino
- Built-in LED (pin 13) blinks on and off
- Console shows "LED ON" / "LED OFF" messages

**Troubleshooting:**
- **No connection**: Check USB cable, verify Arduino is powered
- **Permission error**: Run `sudo chmod 666 /dev/ttyACM0` (Linux)
- **Wrong UUID**: Make sure `TEST_UUID` matches Arduino's `MY_UUID`

### Step 3: Comprehensive Hardware Test

Use `hardware_test.py` for thorough testing:

```bash
python3 hardware_test.py
```

#### Configuration

Edit these sections in `hardware_test.py`:

```python
# Which Arduino to test
TEST_ARDUINO_UUID = 1

# Define your output pins (LEDs, relays, etc.)
TEST_OUTPUT_PINS = [
    (3, PinMode.DIGITAL_OUT, "LED on pin 3"),
    (5, PinMode.DIGITAL_OUT, "LED on pin 5"),
    # Add your pins here
]

# Define your input pins (buttons, sensors)
TEST_INPUT_PINS = [
    (2, PinMode.DIGITAL_IN, "Button on pin 2"),
    (4, PinMode.DIGITAL_IN, "Button on pin 4"),
    # Add your pins here
]

# Serial ports to scan (adjust for your OS)
SERIAL_PORTS = ["/dev/ttyACM" + str(i) for i in range(10)]  # Linux
# SERIAL_PORTS = ["/dev/cu.usbmodem" + str(i) for i in range(10)]  # macOS
# SERIAL_PORTS = ["COM" + str(i) for i in range(1, 20)]  # Windows
```

#### Test Menu Options

1. **Test individual output pin** - Toggle a specific LED/relay
2. **Test all outputs** - Cycle through all outputs
3. **Run blinking pattern** - Synchronized blink test
4. **Monitor inputs** - Watch button presses in real-time
5. **Interactive control** - Manually toggle outputs
6. **Show configuration** - Display current pin states

## Common Testing Scenarios

### Testing a New Arduino Board

1. Flash `sensors.ino` with unique UUID
2. Run `quick_test.py` to verify connection
3. Configure your pins in `hardware_test.py`
4. Test each output pin individually
5. Test each input pin with monitoring mode
6. Document working configuration

### Testing Button Inputs

```python
# In hardware_test.py, add:
TEST_INPUT_PINS = [
    (2, PinMode.DIGITAL_IN, "Red button"),
    (4, PinMode.DIGITAL_IN, "Blue button"),
]

# Run the test:
# - Select option 4 (Monitor inputs)
# - Press buttons and watch console output
# - Verify state changes are detected
```

**Expected behavior:**
- Button NOT pressed: State = HIGH
- Button pressed: State = LOW (if using INPUT_PULLUP)

### Testing LED Outputs

```python
# In hardware_test.py, add:
TEST_OUTPUT_PINS = [
    (3, PinMode.DIGITAL_OUT, "Red LED"),
    (5, PinMode.DIGITAL_OUT, "Green LED"),
]

# Run the test:
# - Select option 1 (Test individual output)
# - Watch LED turn on when state = LOW
# - Watch LED turn off when state = HIGH
```

**Note:** With standard LED wiring (cathode to ground), LOW = ON, HIGH = OFF.

### Testing Color Sensors

```python
TEST_INPUT_PINS = [
    (7, PinMode.PULSE_IN, "Color sensor S2"),
]

# Monitor the sensor and trigger it with colored objects
# PULSE_IN uses pulseIn() to measure pulse width
```

## Understanding Debouncing

Buttons can "bounce" - send multiple rapid signals when pressed. The `InputPin` class handles this automatically:

```python
InputPin(arduino, 2, PinMode.DIGITAL_IN, handler,
         num_collect=8,    # Buffer size
         thresh=0.99)      # 99% of last 8 readings must agree
```

**How it works:**
- Last 8 readings are stored
- State only changes when ≥99% agree
- Prevents false triggers from button bounce

## Pin Numbering Reference

| Arduino Board | Digital Pins | Analog Pins | Built-in LED |
|---------------|--------------|-------------|--------------|
| Arduino Uno | 0-13 | A0-A5 (14-19) | 13 |
| Arduino Mega | 0-53 | A0-A15 (54-69) | 13 |
| Arduino Nano | 0-13 | A0-A7 (14-21) | 13 |

## Integration with Your Application

Once hardware is tested, integrate into `sensors_config.py`:

```python
# Create Arduino objects
arduino1 = Arduino(1)  # UUID must match sensors.ino
arduino2 = Arduino(2)

# Define outputs
lights = [
    OutputPin(arduino1, 3, PinMode.DIGITAL_OUT, initial_value=HIGH),
    OutputPin(arduino1, 5, PinMode.DIGITAL_OUT, initial_value=HIGH),
]

# Define inputs with handlers
def make_button_handler(id):
    def handler(state):
        if state == LOW:  # Button pressed
            YC.send(SHEPHERD_HEADER.BUTTON_PRESS(id=id))
    return handler

buttons = [
    InputPin(arduino1, 2, PinMode.DIGITAL_IN, make_button_handler(0)),
    InputPin(arduino1, 4, PinMode.DIGITAL_IN, make_button_handler(1)),
]

# Start communication
start_device_handlers(
    ["/dev/ttyACM" + str(a) for a in range(10)],
    [arduino1, arduino2]
)
```

## Troubleshooting

### Connection Issues

**Problem:** "PermissionError on /dev/ttyACM0"
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# OR temporarily:
sudo chmod 666 /dev/ttyACM0
```

**Problem:** "Failed handshake - please unplug device"
- Wrong UUID in Arduino code
- Old version of sensors.ino flashed
- Corrupted serial connection

**Problem:** Arduino not detected
- Check USB cable (must be data cable, not power-only)
- Try different USB port
- Check Arduino is powered (LED should be on)
- Verify correct serial port pattern for your OS

### Pin Issues

**Problem:** Output pin doesn't change
- Verify pin number is correct
- Check wiring (LED orientation, resistor)
- Try the built-in LED (pin 13) first
- Use multimeter to test pin voltage

**Problem:** Input pin always reads same value
- Check pull-up resistor configuration
- Verify button wiring (should connect pin to GND)
- Test with jumper wire (manually connect to GND)

**Problem:** Button triggers multiple times
- Increase `thresh` parameter in InputPin
- Increase `num_collect` for more debouncing
- Check for loose wiring

### Timing Issues

**Problem:** Slow response
- Reduce `poll_delay_ms` in Arduino constructor
- Check for blocking code in handlers
- Verify serial baud rate matches (9600)

## Next Steps

1. **Test each Arduino individually** using `hardware_test.py`
2. **Document your pin assignments** (create a wiring diagram)
3. **Verify all hardware** before integrating into main application
4. **Update sensors_config.py** with tested configuration
5. **Run integrated tests** with your YDL system

## Files Reference

- `sensors.ino` - Arduino firmware (flash to each board)
- `sensors.py` - Communication library (don't modify)
- `quick_test.py` - Basic connectivity test
- `hardware_test.py` - Comprehensive test suite (modify configuration section)
- `sensors_config.py` - Your production configuration
- `test_sensors_config.py` - Your existing test file

## Support

If you encounter issues not covered here:
1. Check Arduino Serial Monitor for debug output
2. Add `print()` statements to see data flow
3. Test with minimal configuration (one pin at a time)
4. Verify physical connections with multimeter
