from amaranth import *
from amaranth.build import *
from IceLogicDeck import *

leds12_tile = [
    Resource("leds12", 0,
            Subsignal("leds", Pins("1 2 3 4 5 6 7 8 9 10 11 12", dir="o", conn=("tile",2)), Attrs(IO_STANDARD="SB_LVCMOS")))
]

class LEDTileTest(Elaboratable):
    def elaborate(self, platform):
        leds12 = Cat([l for l in platform.request("leds12")])
        timer = Signal(38)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        m.d.comb += leds12.eq(timer[-15:-1])
        return m


if __name__ == "__main__":
    platform = IceLogicDeckPlatform()
    platform.add_resources(leds12_tile)
    platform.build(LEDTileTest(), do_program=True)