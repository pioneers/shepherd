#include "Arduino2.h"

const int Arduino2::NUM_LINEBREAKS = 4;
const int Arduino2::NUM_BUTTONS = 1;
const int Arduino2::NUM_LIGHTS = 1;

const uint8_t Arduino2::pins[] = {
    2, // desert_linebreak
    4, // dehydration_linebreak
    6, // hypothermia_linebreak
    8, // hypothermia_linebreak
    10, // fire_lever
    14, // fire_light
};

// Constructor is called once and immediately when the Arduino is plugged in
Arduino2::Arduino2() : Device(DeviceType::Arduino2, 13) {
}

size_t Arduino2::device_read(uint8_t param, uint8_t* data_buf) {
    // put pin value into data_buf
    if (param < Arduino2::NUM_LINEBREAKS) {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 0 : 1;
    }
    else if (param < Arduino2::NUM_LINEBREAKS + Arduino2::NUM_BUTTONS) {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 1 : 0;
    } else {
        this->msngr->lowcar_printf("Should not be reading from a light. param is %d", param);
        return 0;
    }

    static uint64_t last_update_time[] = {0, 0, 0, 0, 0, 0};
    uint64_t curr = millis();

    // log each button every 500ms
    if (curr - last_update_time[param] > 500) {
        this->msngr->lowcar_printf("param %d is %s", param, data_buf[0] == 1 ? "true" : "false");
        last_update_time[param] = curr;
    }

    return sizeof(uint8_t);
}

size_t Arduino2::device_write(uint8_t param, uint8_t* data_buf) {
    int min_index = Arduino2::NUM_LINEBREAKS + Arduino2::NUM_BUTTONS;
    if (param <  min_index|| 
        param >= min_index + Arduino2::NUM_LIGHTS) {
        this->msngr->lowcar_printf("Trying to write to something that is not fire light.");
        return 0;
    }

    if (data_buf[0] > 1) {
        this->msngr->lowcar_printf("data_buf[0] is %d, but can only be 0 or 1.", data_buf[0]);
    }

    digitalWrite(Arduino2::pins[param], data_buf[0] == 1 ? HIGH: LOW);
    digitalWrite(Arduino2::pins[param], LOW);

    return 0;
}

void Arduino2::device_enable() {
    this->msngr->lowcar_printf("ARDUINO 2 ENABLING");
    // set all pins to INPUT mode
    int num_inputs = Arduino2::NUM_LINEBREAKS + Arduino2::NUM_BUTTONS;
    for (int i = 0; i < num_inputs; i++) {
        pinMode(Arduino2::pins[i], INPUT);
    }

    for (int i = 0; i < Arduino2::NUM_LIGHTS; i++) {
        pinMode(Arduino2::pins[i + num_inputs], OUTPUT);
    }
}

void Arduino2::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 2 DISABLED");
}

void Arduino2::device_actions() {
    /*
    static uint64_t last_update_time = 0;
    // static uint64_t last_count_time = 0;
    uint64_t curr = millis();

    // Simulate read-only params changing
    if (curr - last_update_time > 500) {
        this->runtime += 2;
        this->shepherd += 1.9;
        this->dawn = !this->dawn;

        this->devops++;
        this->atlas += 0.9;
        this->infra = TRUE;

        // this->msngr->lowcar_print_float("funtime", this->funtime);
        // this->msngr->lowcar_print_float("atlas", this->atlas);
        // this->msngr->lowcar_print_float("pdb", this->pdb);

        last_update_time = curr;
    }

    // this->dusk++;
    //
    // 	//use dusk as a counter to see how fast this loop is going
    // 	if (curr - last_count_time > 1000) {
    // 		last_count_time = curr;
    // 		this->msngr->lowcar_printf("loops in past second: %d", this->dusk);
    // 		this->dusk = 0;
    // 	}
    */
}
