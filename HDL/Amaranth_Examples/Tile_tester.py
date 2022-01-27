from amaranth import *
from amaranth.build import *
from IceLogicDeck import *


leds12_tile = [
    Resource("leds12", 0,

            Subsignal("leds", Pins("1 2 3 4 5 6 7 8 9 10 11 12", dir="o", conn=("tile", 3)), Attrs(IO_STANDARD="SB_LVCMOS")))
]


class LEDTileTest(Elaboratable):
    def elaborate(self, platform):

        leds12 = Cat([l for l in platform.request("leds12")])
        timer = Signal(38)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        m.d.comb += leds12.eq(timer[-15:-1])
        return m


class QSPIE2LedTest(Elaboratable):
    def elaborate(self, platform):
        leds12 = Cat([l for l in platform.request("leds12")])
        qspie = Cat(platform.request("qd0").i,
                   platform.request("qd1").i,
                   platform.request("qd2").i,
                   platform.request("qd3").i,
                   platform.request("qck"),
                   platform.request("qss"),
                   platform.request("qdr"),
                    Repl(C(0, 1), 5))

        m = Module()

        m.d.comb += leds12.eq(qspie)
        return m

if __name__ == "__main__":
    platform = IceLogicDeckPlatform()
    platform.add_resources(leds12_tile)
    # platform.build(LEDTileTest(), do_program=True)
    platform.build(LEDTileTest(), do_program=True)
