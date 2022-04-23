#include "Arduino1.h"

// number of switches on a limit switch (how many input pins)
const int Arduino1::NUM_LIGHTS = 3;
const int Arduino1::NUM_BUTTONS = 1;

const uint8_t Arduino1::pins[] = {
    3, // button lights
    5, // corner lights
    7, // midline lights
    2, // button 1
};

// Constructor is called once and immediately when the Arduino is plugged in
Arduino1::Arduino1() : Device(DeviceType::ARDUINO1, 13) {
}

size_t Arduino1::device_read(uint8_t param, uint8_t* data_buf) {
    if (param < Arduino2::NUM_LIGHTS) {
        this->msngr->lowcar_printf("Sorry, can only read from buttons. Please check your shepherd_util.c");
        return 0;
    }
    data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? TRUE : FALSE;

    // static uint64_t last_update_time[] = {0, 0, 0, 0, 0, 0, 0};
    // uint64_t curr = millis();

    // // log each button every 500ms
    // if (curr - last_update_time[param] > 500) {
    //     // this->msngr->lowcar_printf("button %d is %s", param, data_buf[0] == 1 ? "pressed" : "not pressed");
    //     last_update_time[param] = curr;
    // }
    return sizeof(uint8_t);
}

// writable, not readable. should just call device_write id hope.
size_t Arduino1::device_write(uint8_t param, uint8_t* data_buf) {
    if (data_buf[0] == 1) {
        digitalWrite(Arduino1::pins[param], HIGH);
        this->msngr->lowcar_printf("Wrote %s to %d", "HIGH", Arduino1::pins[param]);
    }
    else {
        digitalWrite(Arduino1::pins[param], LOW);
        this->msngr->lowcar_printf("Wrote %s to %d", "LOW", Arduino1::pins[param]);
    }
    return sizeof(uint8_t);
}

void Arduino1::device_enable() {
    // todo: ask ben what is diff between device enable and constructor
    this->msngr->lowcar_printf("ARDUINO 1 ENABLING");

    for (int i = 0; i < Arduino2::NUM_LIGHTS; i++) {
        pinMode(Arduino2::pins[i], OUTPUT);
    }
    for(int j = Arduino2::NUM_LIGHTS; j < Arduino2::NUM_LIGHTS + Arduino2::NUM_BUTTONS; j++) {
        pinMode(Arduino2::pins[j], INPUT)
    }
}

void Arduino1::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 1 DISABLED");
}

void Arduino1::device_actions() {
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
