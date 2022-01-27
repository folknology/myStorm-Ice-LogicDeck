# Hardware
The Ice LogicDeck (ILD) Hardware consists of modular tiles fitted to the main carrier board as required for the given development project. Onboard the main ILD carrier board are the Microcontroller, the FPGA some SPI Flash and connectors.

The ILD has two Usb connectors, the first is a Usb-C configured as a USB CDC serial device. This can allow programming of the microcontroller, FPGA and flash, along with uart and monitoring features depending on the required mode.

There is a second Usb-C (Usb-PD) Connector which operates as a high Power over Usb 
delivery system operating from 5 to 20 volts in order to be able to power a large range of modular tiles from simple led drivers through to small motor and power-train devices. An auxiliary power supply scheme is also  provided for the more extreme power delivery requirements across the tiles.

Mode selection is achieved via the 'Mode' button, if depressed on power up it switches the device into USB-DFU mode which enables the firmware to be updated from the PC host. Normal startup places the device into development mode. In development mode the device intelligently listens to Usb traffic for either instructions, new deck application,FPGA updates, tests or combinations of those.

A third 'Flash' mode can be entered pressing the mode button during normal operation. This mode enables applications, synthesis or test data to be made permanent inside flash. One can escape this mode back to normal by pressing the  mode button once more.

There is an RGB led on board which can provide feedback and status of the board's mode and operation. In normal mode this is unlit. if and application or FPGA image is uploaded it will change to red and extinguish on successful completion. If it remains red it will normally be due to either a hardware fault or bad FPGA synthesis. If the mode changes it will illuminate green and change to amber during programing and back to green afterwards, again if it remains amber it will likely be a fault. A third state is possible when the FPGA synthesis drives the blue part of the led for example in a blinky test, the colour will the blink between the either blue and off or blue and the mode colour probably blue and turquoise.

There is also a 1.27mm pitch 10pin, Arm SWD debug socket adjacent to the Usb-PD if you need to debug what is running on the Microcontroller.

In addition to the modular tiles there is an optional Mezzanine Tile which can expand the ILD to add useful features like extra RAM, flash, lcd display and Wi-Fi among other things, check out the [Mezzanine](./mezzanine.md) section for more information of these options.

Setting up Ice LogicDeck - Drivers and firmware:
- [DFU](./dfu_util.md)
- [USB-CDC](./usbcdc.md)
- [Power Delivery](./usbpd.md)