from amaranth import *
from IceLogicDeck import *


class Blink(Elaboratable):
    def elaborate(self, platform):
        led = platform.request("led")
        timer = Signal(24)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        m.d.comb += led.eq(timer[-1])
        return m


if __name__ == "__main__":
    platform = IceLogicDeckPlatform()
    platform.build(Blink(), do_program=True)