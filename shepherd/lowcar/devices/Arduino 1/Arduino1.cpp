#include "DummyDevice.h"

// The numbering of each parameter
typedef enum {
    BUTTON1 = 0,
    BUTTON2 = 1,
    BUTTON3 = 2,
    BUTTON4 = 3
} param;

Arduino1::Arduino1() : Device(DeviceType::DUMMY_DEVICE, 13) {
    this->button1 = 1;
}

size_t DummyDevice::device_read(uint8_t param, uint8_t* data_buf) {
    float* float_buf = (float*) data_buf;
    int32_t* int_buf = (int32_t*) data_buf;
    data_buf[0] = this->button1;
    return sizeof(uint8_t); // 8?
    // switch (param) {
    //     case BUTTON1:
    //         int_buf[0] = this->runtime;
    //         return sizeof(this->runtime);
    // }
    return 0;
}

size_t DummyDevice::device_write(uint8_t param, uint8_t* data_buf) {
    switch (param) {
        case RUNTIME:
            break;

        case SHEPHERD:
            break;

        case DAWN:
            break;

        case DEVOPS:
            break;

        case ATLAS:
            break;

        case INFRA:
            break;

        case SENS:
            this->sens = ((int32_t*) data_buf)[0];
            return sizeof(this->sens);

        case PDB:
            this->pdb = ((float*) data_buf)[0];
            return sizeof(this->pdb);

        case MECH:
            this->mech = data_buf[0];
            return sizeof(this->mech);

        case CPR:
            this->cpr = ((int32_t*) data_buf)[0];
            return sizeof(this->cpr);

        case EDU:
            this->edu = ((float*) data_buf)[0];
            return sizeof(this->edu);

        case EXEC:
            this->exec = data_buf[0];
            return sizeof(this->exec);

        case PIEF:
            this->pief = ((int32_t*) data_buf)[0];
            return sizeof(this->pief);

        case FUNTIME:
            this->funtime = ((float*) data_buf)[0];
            return sizeof(this->funtime);

        case SHEEP:
            this->sheep = data_buf[0];
            return sizeof(this->sheep);

        case DUSK:
            this->dusk = ((int32_t*) data_buf)[0];
            return sizeof(this->dusk);
    }
    return 0;
}

void DummyDevice::device_enable() {
    this->msngr->lowcar_printf("ARDUINO 1 ENABLED");
}

void DummyDevice::device_disable() {
    this->msngr->lowcar_printf("ARDUINO 2 DISABLED");
}

void DummyDevice::device_actions() {
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
}
