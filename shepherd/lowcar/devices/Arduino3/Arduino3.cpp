#include "Arduino3.h"

const int Arduino3::NUM_LINEBREAKS = 2;
const int Arduino3::NUM_BUTTONS = 1;
const int Arduino3::NUM_LIGHTS = 1;

const uint8_t Arduino3::pins[] = {
    2, // city_linebreak
    4, // traffic_linebreak
    7, // traffic_button
    6, // traffic_light
};

// Constructor is called once and immediately when the Arduino is plugged in
Arduino3::Arduino3() : Device(DeviceType::Arduino3, 13) {
}

size_t Arduino3::device_read(uint8_t param, uint8_t* data_buf) {
    // put pin value into data_buf and return the amount of bytes written
    /* 
        is robot currently breaking line break?
        currently, its no. then it goes through and eventually turns to yes. 
        then its no.
    */
    if (param < Arduino3::NUM_LINEBREAKS) {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 0 : 1;
    }
    else if (param < Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS) {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 1 : 0;
    } else {
        this->msngr->lowcar_printf("Should not be reading from a light. param is %d", param);
        return 0;
    }

    static uint64_t last_update_time[] = {0, 0, 0};
    uint64_t curr = millis();

    // log each button every 500ms
    if (curr - last_update_time[param] > 500) {
        this->msngr->lowcar_printf("param %d is %s", param, data_buf[0] == 1 ? "true" : "false");
        last_update_time[param] = curr;
    }

    return sizeof(uint8_t);
}

size_t Arduino3::device_write(uint8_t param, uint8_t* data_buf) {
    int min_index = Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS;
    if (param < min_index || param >= min_index + Arduino3::NUM_LIGHTS) {
        this->msngr->lowcar_printf("Trying to write to something that is not fire light.");
        return 0;
    }
    
   if (data_buf[0] > 1) {
        this->msngr->lowcar_printf("data_buf[0] is %d, but can only be 0 or 1.", data_buf[0]);
    }

    digitalWrite(Arduino3::pins[param], data_buf[0] == 1 ? HIGH: LOW);
    digitalWrite(Arduino3::pins[param], LOW);

    return 0;
}

void Arduino3::device_enable() {
    // todo: ask ben what is diff between device enable and constructor
    this->msngr->lowcar_printf("ARDUINO 3 ENABLING");
    // set all pins to INPUT mode
    int num_inputs = Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS;
    for (int i = 0; i < num_inputs; i++) {
        pinMode(Arduino3::pins[i], INPUT);
    }

    for (int i = 0; i < Arduino3::NUM_LIGHTS; i++) {
        pinMode(Arduino3::pins[i + num_inputs], OUTPUT);
    }
}

void Arduino3::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 3 DISABLED :(");
}

void Arduino3::device_actions() {
}
