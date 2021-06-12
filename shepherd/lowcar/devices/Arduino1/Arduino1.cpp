#include "Arduino1.h"

// number of switches on a limit switch (how many input pins)
const int Arduino1::NUM_BUTTONS = 7;
const int Arduino1::NUM_LIGHTS = 7;
/*
button1: 2
light1: 3
button2: 4
light2: 5
button3: 6
light3: 7
button4: 8
light4: 9
button5: 10
light5: A0
button6: 14
light6: A1
button7: 15
light7: A2
*/
const uint8_t Arduino1::pins[] = {
    // buttons 1 - 7
    2,
    4,
    6,
    8,
    10,
    12,
    13,
    // lights 1 - 7
    3,
    5,
    7,
    9,
    11,
    A0,
    A1
};

// Constructor is called once and immediately when the Arduino is plugged in
Arduino1::Arduino1() : Device(DeviceType::ARDUINO1, 13) {
}

size_t Arduino1::device_read(uint8_t param, uint8_t* data_buf) {
    // put pin value into data_buf and return the amount of bytes written
    if (param >= Arduino1::NUM_BUTTONS) {
        // this->msngr->lowcar_printf("Sorry, can only read from buttons. Please check your shepherd_util.c");
        return 0;
    }
    data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? TRUE : FALSE;

    static uint64_t last_update_time[] = {0, 0, 0, 0, 0, 0, 0};
    uint64_t curr = millis();

    // log each button every 500ms
    if (curr - last_update_time[param] > 500) {
        // this->msngr->lowcar_printf("button %d is %s", param, data_buf[0] == 1 ? "pressed" : "not pressed");
        last_update_time[param] = curr;
    }

    return sizeof(uint8_t);
}
// writable, not readable. should just call device_write id hope.
size_t Arduino1::device_write(uint8_t param, uint8_t* data_buf) {
    if (param < Arduino1::NUM_BUTTONS) {
        // this->msngr->lowcar_printf("Should not be writing to buttons.");
        return 0;
    }
    if (data_buf[0] == 1) {
        digitalWrite(Arduino1::pins[param], HIGH);
        // this->msngr->lowcar_printf("Wrote %s to %d", "HIGH", Arduino1::pins[param]);
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

    // set all pins to INPUT mode
    for (int i = 0; i < Arduino1::NUM_BUTTONS; i++) {
        pinMode(Arduino1::pins[i], INPUT);
    }

    for (int i = 0; i < Arduino1::NUM_LIGHTS; i++) {
        pinMode(Arduino1::pins[i + NUM_BUTTONS], OUTPUT);
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
