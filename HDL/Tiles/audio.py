from amaranth import *
from amaranth.build import *


class SquareWave(Elaboratable):
    def __init__(self):
        self.left = Signal()
        self.right = Signal()


    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        timer = Signal(16)
        m.d.sync += timer.eq(timer + 1)
        m.d.comb += [
            self.left.eq(timer[-2]),
            self.right.eq(timer[-3])
        ]

        return m
