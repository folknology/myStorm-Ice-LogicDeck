from typing import List, Dict

from amaranth import *
from amaranth.build import *
from IceLogicDeck import *
from seven_seg import SevenSegController

TILE = 1
PINMAP = {"a": "6", "b": "8", "c": "12", "d": "10", "e": "7", "f": "5", "g": "4", "dp": "9", "ca": "3 2 1"}

subSignals = [
    Subsignal(signal,
              Pins(pin, invert=True, dir="o", conn=("tile", TILE)),
              Attrs(IO_STANDARD="SB_LVCMOS")
              ) for signal, pin in PINMAP.items()
]

seven_seg_tile = [
    Resource("seven_seg", 0, *subSignals)
]


class SevenSegTest(Elaboratable):
    def elaborate(self, platform):
        # Get pins
        seg_pins = platform.request("seven_seg")
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d,
                     seg_pins.e, seg_pins.f, seg_pins.g])

        # Add 7-segment controller
        m = Module()
        m.submodules.seven = seven = SevenSegController()

        # Timer
        timer = Signal(40)
        m.d.sync += timer.eq(timer + 1)

        # Connect pins
        m.d.comb += [
            leds7.eq(seven.leds)
        ]

        # Set pins for each digit to appropriate slice of time to count up in hex
        for i in range(3):
            # Each digit refreshed at at least 100Hz
            m.d.comb += seg_pins.ca[i].eq(timer[17:19] == i)

            with m.If(seg_pins.ca[i]):
                m.d.comb += seven.val.eq(timer[((i - 3) * 4) - 5:((i - 3) * 4) - 1])

        return m


if __name__ == "__main__":
    platform = IceLogicDeckPlatform()
    platform.add_resources(seven_seg_tile)
    platform.build(SevenSegTest(), do_program=True)