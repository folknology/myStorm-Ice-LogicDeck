from amaranth import *
from amaranth.build import *

from mystorm_boards.icelogicbus import *

BLADE = 4

led_blade = [
    Resource("leds6", 0,
                Subsignal("leds",
                          Pins("1 2 3 4 5 6", dir="o", conn=("blade", BLADE)),
                          Attrs(IO_STANDARD="SB_LVCMOS")
                          )
             )
]

class LedBlade(Elaboratable):

    def elaborate(self, platform):
        leds6 = Signal(6, reset = 0b1111)
        leds6 = Cat([l for l in platform.request("leds6")])
        timer = Signal(23)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        with m.If(timer[-1]):
            m.d.sync += leds6.eq(Cat(leds6[1:6], ~leds6[0]))

        return m

def synth():
    platform = IceLogicBusPlatform()
    platform.add_resources(led_blade)
    platform.build(LedBlade(), do_program=True)
