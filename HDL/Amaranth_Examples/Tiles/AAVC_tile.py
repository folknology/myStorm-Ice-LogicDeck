from typing import List

from amaranth import *
from amaranth.build import *
from .vga import *

PINMAP = {"hs": "3", "vs": "4", "red": "11 7 6", "green": "12 10 5", "blue": "9 8", "right": "2", "left": "1"}


def tile_resources(tile: int) -> List:
    signals = [
        Subsignal(signal,
                  Pins(pin, invert=False, dir="o", conn=("tile", tile)),
                  Attrs(IO_STANDARD="SB_LVCMOS")
                  ) for signal, pin in PINMAP.items()
    ]

    return [Resource("av_tile", 0, *signals)]

# Analogue Audio Video Controller
class AAVController(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        m = Module()

        return m
