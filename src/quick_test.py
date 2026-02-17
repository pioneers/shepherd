#!/usr/bin/env python3
"""
Quick Arduino Connectivity Test

This is a minimal test to verify Arduino is connected and responding.
Blinks the built-in LED (pin 13) if available.

Usage:
    1. Edit TEST_UUID to match your Arduino's UUID in sensors.ino
    2. Run: python3 quick_test.py
    3. Watch for connection confirmation and LED blinking
"""

import time
from sensors import PinMode, DigitalValue, Arduino, OutputPin, start_device_handlers

# ============= CONFIGURATION =============
TEST_UUID = 1  # Change this to match MY_UUID in your sensors.ino
TEST_PIN = 8  # Built-in LED on most Arduinos
SERIAL_PORTS = ["/dev/ttyACM" + str(i) for i in range(10)]  # Adjust for your OS
# =========================================

LOW = DigitalValue.LOW.value
HIGH = DigitalValue.HIGH.value

print("=" * 60)
print("QUICK ARDUINO CONNECTIVITY TEST")
print("=" * 60)
print(f"Testing Arduino UUID: {TEST_UUID}")
print(f"Test pin: {TEST_PIN}")
print(f"Scanning: {SERIAL_PORTS[0]} to {SERIAL_PORTS[-1]}")
print("\nMake sure:")
print("  1. Arduino is plugged in via USB")
print("  2. sensors.ino is flashed with MY_UUID = {TEST_UUID}")
print("  3. No other programs are using the serial port")
print("=" * 60)

# Create Arduino and test pin
arduino = Arduino(TEST_UUID)
led = OutputPin(arduino, TEST_PIN, PinMode.DIGITAL_OUT, initial_value=HIGH)

# Start handlers
print("\nStarting communication...")
start_device_handlers(SERIAL_PORTS, [arduino])

# Wait for connection
print("Waiting for Arduino to connect (this may take a few seconds)...")
time.sleep(4)

print("\n" + "=" * 60)
print("CONNECTION ESTABLISHED!")
print("=" * 60)
print(f"\nIf you see this, the handshake was successful!")
print(f"Now blinking LED on pin {TEST_PIN}...\n")

# Blink LED
try:
    cycle = 0
    while True:
        cycle += 1
        led.set_state(LOW)  # Turn ON
        print(f"Cycle {cycle}: LED ON  (pin state = LOW)")
        time.sleep(0.5)

        led.set_state(HIGH)  # Turn OFF
        print(f"Cycle {cycle}: LED OFF (pin state = HIGH)")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n\nTest stopped by user.")
    print("If you saw the LED blinking, your Arduino is working correctly!")
    print("\nNext steps:")
    print("  - Use hardware_test.py for comprehensive testing")
    print("  - Configure your actual pins in sensors_config.py")
