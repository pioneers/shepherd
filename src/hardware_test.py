#!/usr/bin/env python3
"""
Hardware Test Suite for Arduino System

This script helps you test individual Arduinos and their connected peripherals.
It provides an interactive menu to test inputs, outputs, and verify connections.

Usage:
    python3 hardware_test.py
"""

import time
from sensors import PinMode, DigitalValue, Arduino, InputPin, OutputPin, start_device_handlers

# Digital value constants
LOW = DigitalValue.LOW.value
HIGH = DigitalValue.HIGH.value

# ============================================================================
# CONFIGURATION SECTION - Modify this for your test setup
# ============================================================================

# Change this to match the Arduino you're testing
TEST_ARDUINO_UUID = 1

# Define your test pins here
# Format: (pin_number, pin_mode, description)
TEST_OUTPUT_PINS = [
    (3, PinMode.DIGITAL_OUT, "LED on pin 3"),
    (5, PinMode.DIGITAL_OUT, "LED on pin 5"),
    (7, PinMode.DIGITAL_OUT, "LED on pin 7"),
    (13, PinMode.DIGITAL_OUT, "Built-in LED (if available)"),
]

TEST_INPUT_PINS = [
    (2, PinMode.DIGITAL_IN, "Button on pin 2"),
    (4, PinMode.DIGITAL_IN, "Button on pin 4"),
]

# Serial port patterns to scan (adjust for your OS)
# Linux: ["/dev/ttyACM" + str(i) for i in range(10)]
# macOS: ["/dev/cu.usbmodem" + str(i) for i in range(10)]
# Windows: ["COM" + str(i) for i in range(1, 20)]
SERIAL_PORTS = ["/dev/ttyACM" + str(i) for i in range(10)]

# ============================================================================
# TEST IMPLEMENTATION
# ============================================================================

class HardwareTest:
    def __init__(self):
        self.arduino = Arduino(TEST_ARDUINO_UUID, poll_delay_ms=10)
        self.output_pins = []
        self.input_pins = []
        self.input_states = {}
        self.connected = False

        print("=" * 70)
        print("ARDUINO HARDWARE TEST SUITE")
        print("=" * 70)
        print(f"\nTesting Arduino UUID: {TEST_ARDUINO_UUID}")
        print(f"Scanning serial ports: {SERIAL_PORTS[0]} through {SERIAL_PORTS[-1]}")

        # Set up output pins
        print(f"\nConfiguring {len(TEST_OUTPUT_PINS)} output pins:")
        for pin_num, pin_mode, description in TEST_OUTPUT_PINS:
            output_pin = OutputPin(self.arduino, pin_num, pin_mode, initial_value=HIGH)
            self.output_pins.append((output_pin, pin_num, description))
            print(f"  - Pin {pin_num}: {description}")

        # Set up input pins with handlers
        print(f"\nConfiguring {len(TEST_INPUT_PINS)} input pins:")
        for pin_num, pin_mode, description in TEST_INPUT_PINS:
            handler = self._make_input_handler(pin_num, description)
            input_pin = InputPin(self.arduino, pin_num, pin_mode, handler)
            self.input_pins.append((input_pin, pin_num, description))
            self.input_states[pin_num] = None
            print(f"  - Pin {pin_num}: {description}")

        # Start device handlers
        print("\nStarting device handlers...")
        start_device_handlers(SERIAL_PORTS, [self.arduino])

        # Wait for connection
        print("\nWaiting for Arduino to connect...")
        print("(Make sure Arduino is plugged in and has the correct UUID)")
        time.sleep(3)
        self.connected = True
        print("\nReady to test!\n")

    def _make_input_handler(self, pin_num, description):
        """Create a callback function for input pins"""
        def handler(state):
            state_str = "LOW (pressed)" if state == LOW else "HIGH (released)"
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Pin {pin_num} ({description}): {state_str}")
            self.input_states[pin_num] = state
        return handler

    def test_output_pin(self, index):
        """Test a specific output pin by toggling it"""
        if index < 0 or index >= len(self.output_pins):
            print(f"Invalid pin index. Choose 0-{len(self.output_pins)-1}")
            return

        pin, pin_num, description = self.output_pins[index]
        print(f"\nTesting: {description} (Pin {pin_num})")
        print("Toggling HIGH -> LOW -> HIGH (watch for LED/relay change)")

        pin.set_state(HIGH)
        print("  State: HIGH")
        time.sleep(1)

        pin.set_state(LOW)
        print("  State: LOW")
        time.sleep(1)

        pin.set_state(HIGH)
        print("  State: HIGH")
        print("Test complete!\n")

    def test_all_outputs(self):
        """Test all output pins in sequence"""
        print("\nTesting all output pins in sequence...")
        for i in range(len(self.output_pins)):
            self.test_output_pin(i)
            time.sleep(0.5)
        print("All output pins tested!\n")

    def test_output_pattern(self):
        """Run a blinking pattern on all outputs"""
        print("\nRunning blink pattern (10 cycles)...")
        for cycle in range(10):
            # Turn all on
            for pin, _, _ in self.output_pins:
                pin.set_state(LOW)
            time.sleep(0.2)

            # Turn all off
            for pin, _, _ in self.output_pins:
                pin.set_state(HIGH)
            time.sleep(0.2)

            print(f"  Cycle {cycle + 1}/10 complete")
        print("Pattern complete!\n")

    def monitor_inputs(self, duration=10):
        """Monitor all input pins for a specified duration"""
        print(f"\nMonitoring input pins for {duration} seconds...")
        print("Press buttons/trigger sensors now!\n")

        start_time = time.time()
        while time.time() - start_time < duration:
            remaining = int(duration - (time.time() - start_time))
            print(f"\rTime remaining: {remaining}s ", end='', flush=True)
            time.sleep(0.1)

        print("\n\nMonitoring complete!")
        print("Final states:")
        for pin_num, state in self.input_states.items():
            state_str = "LOW" if state == LOW else "HIGH" if state == HIGH else "No data"
            print(f"  Pin {pin_num}: {state_str}")
        print()

    def interactive_control(self):
        """Interactive mode to manually control outputs"""
        print("\nInteractive Control Mode")
        print("Commands:")
        for i, (_, pin_num, desc) in enumerate(self.output_pins):
            print(f"  {i}: Toggle pin {pin_num} ({desc})")
        print("  q: Quit interactive mode\n")

        while True:
            cmd = input("Enter command: ").strip()
            if cmd == 'q':
                break
            try:
                index = int(cmd)
                if 0 <= index < len(self.output_pins):
                    pin, pin_num, desc = self.output_pins[index]
                    # Toggle the pin
                    current = pin.state
                    new_state = LOW if current == HIGH else HIGH
                    pin.set_state(new_state)
                    state_str = "LOW" if new_state == LOW else "HIGH"
                    print(f"Pin {pin_num} ({desc}) set to {state_str}")
                else:
                    print("Invalid pin number")
            except ValueError:
                print("Invalid command")
        print()

    def run_menu(self):
        """Main menu loop"""
        while True:
            print("=" * 70)
            print("HARDWARE TEST MENU")
            print("=" * 70)
            print("1. Test individual output pin")
            print("2. Test all output pins in sequence")
            print("3. Run blinking pattern on outputs")
            print("4. Monitor input pins (buttons/sensors)")
            print("5. Interactive control mode")
            print("6. Show pin configuration")
            print("0. Exit")
            print()

            choice = input("Select option: ").strip()

            if choice == '1':
                print("\nAvailable output pins:")
                for i, (_, pin_num, desc) in enumerate(self.output_pins):
                    print(f"  {i}: Pin {pin_num} - {desc}")
                try:
                    index = int(input("Enter pin index: ").strip())
                    self.test_output_pin(index)
                except ValueError:
                    print("Invalid input\n")

            elif choice == '2':
                self.test_all_outputs()

            elif choice == '3':
                self.test_output_pattern()

            elif choice == '4':
                try:
                    duration = int(input("Monitor duration (seconds, default 10): ").strip() or "10")
                    self.monitor_inputs(duration)
                except ValueError:
                    print("Invalid duration\n")

            elif choice == '5':
                self.interactive_control()

            elif choice == '6':
                self.show_configuration()

            elif choice == '0':
                print("\nExiting test suite. Goodbye!")
                break

            else:
                print("Invalid option\n")

    def show_configuration(self):
        """Display current pin configuration"""
        print("\n" + "=" * 70)
        print("CURRENT CONFIGURATION")
        print("=" * 70)
        print(f"Arduino UUID: {TEST_ARDUINO_UUID}")
        print(f"\nOutput Pins ({len(self.output_pins)}):")
        for pin, pin_num, desc in self.output_pins:
            state_str = "LOW" if pin.state == LOW else "HIGH"
            print(f"  Pin {pin_num:2d}: {desc:30s} [Current: {state_str}]")

        print(f"\nInput Pins ({len(self.input_pins)}):")
        for _, pin_num, desc in self.input_pins:
            state = self.input_states.get(pin_num)
            state_str = "LOW" if state == LOW else "HIGH" if state == HIGH else "No data yet"
            print(f"  Pin {pin_num:2d}: {desc:30s} [Last: {state_str}]")
        print()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        test = HardwareTest()
        test.run_menu()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()
