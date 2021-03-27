#include "Arduino3.h"

// number of switches on a limit switch (how many input pins)
const int Arduino3::NUM_INPUTS = 4;
const int Arduino3::NUM_LIGHTS = 2;
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
const uint8_t Arduino3::pins[] = {
    // 4 pins: 2 city_linebreak, 4 traffic_linebreak, 7 traffic_light, 6 traffic_button
    2,
    4,
    7,
    6,
};

// The numbering of each parameter
// typedef enum {
//     BUTTON1 = 0,
//     BUTTON2 = 1,
//     BUTTON3 = 2,
// } param;

// Constructor is called once and immediately when the Arduino is plugged in
Arduino3::Arduino3() : Device(DeviceType::Arduino3, 13) {
}

size_t Arduino3::device_read(uint8_t param, uint8_t* data_buf) {
    // put pin value into data_buf and return the state of the switch
    if (param < 2) {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 0 : 1;
    }
    else {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 1 : 0;
    }


    // this->msngr->lowcar_printf("button %d is %d", param, data_buf[0]);
    // if (data_buf[0] == true) {
    //     this->led->slow_blink(3);
    // }

    static uint64_t last_update_time[] = {0, 0, 0, 0, 0, 0, 0};
    uint64_t curr = millis();

    // log each button every 500ms
    if (curr - last_update_time[param] > 500) {
        this->msngr->lowcar_printf("button %d is %s", param, data_buf[0] == 1 ? "pressed" : "not pressed");
        last_update_time[param] = curr;
    }

    return sizeof(uint8_t);
}

size_t Arduino3::device_write(uint8_t param, uint8_t* data_buf) {
    // TODO: add some error handling?
    if (param != 2) {
        this->msngr->lowcar_printf("trying to write to something that is not traffic_light");
    }
    else if (data_buf[0] == 1) {
        digitalWrite(Arduino3::pins[param], HIGH);
    }
    else {
        digitalWrite(Arduino3::pins[param], LOW);
    }
    return 0;;
}

void Arduino3::device_enable() {
    // todo: ask ben what is diff between device enable and constructor
    this->msngr->lowcar_printf("ARDUINO 3 ENABLING");
    // set all pins to INPUT mode
    for (int i = 0; i < Arduino3::NUM_INPUTS; i++) {
        pinMode(Arduino3::pins[i], INPUT);
    }

    for (int i = 0; i < Arduino3::NUM_LIGHTS; i++) {
        pinMode(Arduino3::pins[i + NUM_INPUTS], OUTPUT);
    }
}

void Arduino3::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 3 DISABLED");
}

void Arduino3::device_actions() {
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
