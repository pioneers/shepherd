#pragma once

#include "Device.h"
#include "defs.h"
#include "StatusLED.h"

/**
 * write stuff
 */

class Arduino2 : public Device {
  public:
    // construct a Dummy device
    Arduino2();

    virtual size_t device_read(uint8_t param, uint8_t* data_buf);
    virtual size_t device_write(uint8_t param, uint8_t* data_buf);
    virtual void device_enable();
    virtual void device_disable();

    // Changes several of the readable params for testing
    virtual void device_actions();
    private:
      const static int NUM_LINEBREAKS;
      const static int NUM_BUTTONS;
      const static int NUM_LIGHTS;
      // TODO: update pins that the buttons read data from (defined in defs.h)
      const static uint8_t pins[];

      StatusLED* led;

};
