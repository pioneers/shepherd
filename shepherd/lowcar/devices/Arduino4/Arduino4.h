#pragma once

#include "Device.h"
#include "defs.h"
#include "StatusLED.h"

/**
 * write stuff
 */

class Arduino4 : public Device {
  public:
    // construct a Dummy device
    Arduino4();

    virtual size_t device_write(uint8_t param, uint8_t* data_buf);
    virtual void device_enable();
    virtual void device_disable();

    private:
      // number of lasers
      const static int LASERS_PIN;
};
