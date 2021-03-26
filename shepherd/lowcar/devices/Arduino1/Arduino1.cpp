#include "Arduino1.h"

// number of switches on a limit switch (how many input pins)
const int Arduino1::NUM_BUTTONS = 3;
const uint8_t Arduino1::pins[] = {
    (const uint8_t) Analog::IO0,
    (const uint8_t) Analog::IO1,
    (const uint8_t) Analog::IO2};

// The numbering of each parameter
// typedef enum {
//     BUTTON1 = 0,
//     BUTTON2 = 1,
//     BUTTON3 = 2,
// } param;

Arduino1::Arduino1() : Device(DeviceType::ARDUINO1, 13) {
    // stuff here
}

size_t Arduino1::device_read(uint8_t param, uint8_t* data_buf) {
    // put pin value into data_buf and return the state of the switch
    data_buf[0] = (digitalRead(this->pins[param]) == LOW);
    return sizeof(uint8_t);
}

void Arduino1::device_enable() {
    this->msngr->lowcar_printf("ARDUINO 1 ENABLING");
    // set all pins to INPUT mode
    for (int i = 0; i < Arduino1::NUM_BUTTONS; i++) {
        pinMode(Arduino1::pins[i], INPUT);
    }
}

void Arduino1::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 2 DISABLED");
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