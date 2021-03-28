#include "Arduino4.h"

const int Arduino4::LASERS_PIN = 2;

// Constructor is called once and immediately when the Arduino is plugged in
Arduino4::Arduino4() : Device(DeviceType::ARDUINO4, 13) {
}

size_t Arduino4::device_write(uint8_t param, uint8_t* data_buf) {
    digitalWrite(Arduino4::LASERS_PIN, data_buf[0] == 1 ? HIGH: LOW);
    return sizeof(uint8_t);
}

void Arduino4::device_enable() {
    this->msngr->lowcar_printf("ARDUINO 4 ENABLING");
    // set pin to OUTPUT mode
    pinMode(Arduino4::LASERS_PIN, OUTPUT);
}

void Arduino4::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 4 DISABLED :(");
}