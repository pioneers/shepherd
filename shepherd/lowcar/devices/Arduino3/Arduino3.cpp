#include "Arduino3.h"

const int Arduino3::NUM_LINEBREAKS = 2;
const int Arduino3::NUM_BUTTONS = 1;
const int Arduino3::NUM_LIGHT_PINS = 2;

#define S0 5
#define S1 6
#define S2 7
#define S3 8

#define LINEBREAK_THRESHOLD 100

const uint8_t Arduino3::pins[] = {
    9, // city_linebreak
    10, // traffic_linebreak
    4, // traffic_button
    2, // traffic_light on = 1, off = 0
    3, // traffic_light red = 0, green = 1
};
// 2 is red, 3 is green, no pin is off

// Constructor is called once and immediately when the Arduino is plugged in
Arduino3::Arduino3() : Device(DeviceType::ARDUINO3, 13)
{
    for(int i = 0; i < 2; i++) {
    this->prev_red_frequencies[i] = 6000;
    }
}

size_t Arduino3::device_read(uint8_t param, uint8_t *data_buf)
{
    // put pin value into data_buf and return the amount of bytes written
    if (param < Arduino3::NUM_LINEBREAKS)
    {
        // Reading the output frequency
        int redFrequency = pulseIn(Arduino3::pins[param], LOW, 50000);
        
        // we should ignore red frequency == 0 because it is a bug
        if (redFrequency == 0) {
            redFrequency = this->prev_red_frequencies[param];
        }

        if (redFrequency <= LINEBREAK_THRESHOLD && redFrequency > 0)
        {
            data_buf[0] = 0;
        }
        else
        {
            data_buf[0] = 1;
        }
        this->prev_red_frequencies[param] = redFrequency;

        return sizeof(uint8_t);
    }
    else if (param < Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS)
    {
        data_buf[0] = (digitalRead(this->pins[param]) == HIGH) ? 1 : 0;
        return sizeof(uint8_t);
    }
    else
    {
        this->msngr->lowcar_printf("Should not be reading from a light. param is %d", param);
        return 0;
    }

    /*
    static uint64_t last_update_time[] = {0};
    uint64_t curr = millis();

    // log each button every 500ms
    if (curr - last_update_time[param] > 500) {
        this->msngr->lowcar_printf("param %d is %s", param, data_buf[0] == 1 ? "true" : "false");
        last_update_time[param] = curr;
    }
    */
}

size_t Arduino3::device_write(uint8_t param, uint8_t *data_buf)
{
    // this->msngr->lowcar_printf("write called with %d", param);
    int red_pin = 2;
    int green_pin = 3;
    int min_index = Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS;
    int max_index = Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS;
    if (param < min_index || param > min_index)
    {
        this->msngr->lowcar_printf("Trying to write to something that is not the traffic light.");
        return 0;
    }
    int *int_buf = (int *) data_buf;
    int value = int_buf[0];
    if (value == 0)
    {
        // off
        digitalWrite(red_pin, LOW);
        digitalWrite(green_pin, LOW);
        return 4;
    }
    else if (value == 1)
    {
        // red
        digitalWrite(green_pin, LOW);
        digitalWrite(red_pin, HIGH);
        return 4;
    }
    else if (value == 2)
    {
        // green
        digitalWrite(red_pin, LOW);
        digitalWrite(green_pin, HIGH);
        return 4;
    }
    else
    {
        this->msngr->lowcar_printf("Traffic light value must be 0, 1 or 2 but was %d", param);
    }

    return 0;
}

void Arduino3::device_enable()
{
    this->msngr->lowcar_printf("ARDUINO 3 ENABLING");
    // set all pins to INPUT mode
    int num_inputs = Arduino3::NUM_LINEBREAKS + Arduino3::NUM_BUTTONS;
    for (int i = 0; i < num_inputs; i++)
    {
        pinMode(Arduino3::pins[i], INPUT);
    }

    for (int i = 0; i < Arduino3::NUM_LIGHT_PINS; i++)
    {
        pinMode(Arduino3::pins[i + num_inputs], OUTPUT);
    }

    // Setting the outputs
    pinMode(S0, OUTPUT);
    pinMode(S1, OUTPUT);
    pinMode(S2, OUTPUT);
    pinMode(S3, OUTPUT);
    // Setting the sensorOut as an input
    pinMode(this->pins[0], INPUT);
    pinMode(this->pins[1], INPUT);
    // Setting frequency scaling to 20%
    digitalWrite(S0, HIGH);
    digitalWrite(S1, LOW);
    // Setting RED (R) filtered photodiodes to be read
    digitalWrite(S2, LOW);
    digitalWrite(S3, LOW);
}

void Arduino3::device_disable()
{
    this->msngr->lowcar_printf("ARDUINO 3 DISABLED :(");
}
