from amaranth import *
from mystorm_boards.icelogicbus import *


class Blink(Elaboratable):
    def elaborate(self, platform):
        led = platform.request("led")
        # led = platform.request("tx")
        timer = Signal(24)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        m.d.comb += led.eq(timer[-1])
        return m

def synth():
    platform = IceLogicBusPlatform()
    platform.build(Blink(), do_program=True)


if __name__ == "__main__":
    platform = IceLogicBusPlatform()
    platform.build(Blink(), do_program=True)