// change this UUID for every arduino this script is flashed onto
#define MY_UUID 1

#define handshake_magic 2734451328
#define baudrate 9600
#define max_pins 50

#define pinmode_digital_in  0
#define pinmode_pulse_in    1
#define pinmode_digital_out 2
#define pinmode_analog_out  3
#define digital_val_high 0xC3
#define digital_val_low  0x34
#define digital_val_null 0x0F

#define pulsein_threshold 100

// 8 for handshake, or +2 for dummy byte and end of buffer. Did +8 just to be safe
byte msg_buf[max_pins + 8];
byte configuration[2 * max_pins];
byte checksum;
size_t num_pins_used;
size_t num_input_pins;
size_t num_output_pins;

void to_buf(uint32_t x, byte* buf) {
  buf[0] = (x) & 0xFF;
  buf[1] = (x >> 8) & 0xFF;
  buf[2] = (x >> 16) & 0xFF;
  buf[3] = (x >> 24) & 0xFF;
}

void readAllBytes(byte* buffer, size_t length) {
  while (length > 0) {
    size_t n = Serial.readBytes(buffer, length);
    length -= n;
    buffer = &(buffer[n]);
  }
}

void setup() {
  // first part of handshake: send 4 byte magic and 4 byte UUID
  Serial.begin(baudrate);
  while (!Serial); // wait for Serial to initialize
  Serial.setTimeout(1000);
  to_buf(handshake_magic, msg_buf);
  to_buf(MY_UUID, &(msg_buf[4]));
  Serial.write(msg_buf, 8);
  Serial.flush();

  //second part of handshake: receive a 1 byte length, then 2n byte config
  readAllBytes(msg_buf, 1);
  num_pins_used = msg_buf[0];

  if (num_pins_used > max_pins) {
    msg_buf[0] = 0;
    msg_buf[1] = 0;
    Serial.write(msg_buf, 2); // send handshake failure
  } else {
    readAllBytes(configuration, 2 * num_pins_used);
    checksum = 0;
    num_input_pins = 0;
    num_output_pins = 0;
    for (int a = 0; a < num_pins_used; a++) {
      int pin_num = configuration[2*a];
      int pin_mode = configuration[2*a + 1];
      checksum = checksum ^ pin_num ^ pin_mode;
      switch (pin_mode) {
        case pinmode_digital_in:
        case pinmode_pulse_in:
          pinMode(pin_num, INPUT_PULLUP);
          num_input_pins += 1;
          break;
        case pinmode_digital_out:
        case pinmode_analog_out:
          pinMode(pin_num, OUTPUT);
          num_output_pins += 1;
          break;
        default:
          num_pins_used = 0; // handshake failure
          break;
      }
    }
    msg_buf[0] = num_pins_used;
    msg_buf[1] = checksum;
    Serial.write(msg_buf, 2); // send handshake success
  }
}


void loop() {
  // wait for host to send a request
  readAllBytes(msg_buf, 1 + num_output_pins);

  // process all outputs
  int idx = 1; // first byte is dummy
  for (int a = 0; a < num_pins_used; a++) {
    int pin_num = configuration[2*a];
    byte val = msg_buf[idx];
    switch (configuration[2*a + 1]) {
      case pinmode_digital_out:
        if (val == digital_val_high) {digitalWrite(pin_num, HIGH);}
        if (val == digital_val_low)  {digitalWrite(pin_num, LOW);}
        idx += 1;
        break;
      case pinmode_analog_out:
        analogWrite(pin_num, val);
        idx += 1;
        break;
    }
  }

  // process all inputs
  msg_buf[0] = 42; // dummy byte
  idx = 1;
  for (int a = 0; a < num_pins_used; a++) {
    int pin_num = configuration[2*a];
    switch (configuration[2*a + 1]) {
      case pinmode_digital_in:
        msg_buf[idx] = digitalRead(pin_num) == HIGH ? digital_val_high : digital_val_low;
        idx += 1;
        break;
      case pinmode_pulse_in:
        int pulsetime = pulseIn(pin_num, LOW, 50000);
        if (pulsetime == 0) { // timed out
          msg_buf[idx] = digital_val_null;
        } else if (pulsetime < pulsein_threshold) {
          msg_buf[idx] = digital_val_low;
        } else {
          msg_buf[idx] = digital_val_high;
        }
        idx += 1;
        break;
    }
  }
  
  Serial.write(msg_buf, 1 + num_input_pins);
}
