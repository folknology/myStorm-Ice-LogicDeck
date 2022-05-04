from amaranth import *
from amaranth.build import *
from amaranth.hdl.ast import Rose

from mystorm_boards.icelogicbus import *
from HDL.Amaranth_Examples.Tiles.seven_seg_tile import tile_resources


TILE = 3

leds12_tile = [
    Resource("leds12", 0,

            Subsignal("leds", Pins("1 2 3 4 5 6 7 8 9 10 11 12", dir="o", conn=("tile", TILE)), Attrs(IO_STANDARD="SB_LVCMOS")))
]


class LEDTileTest(Elaboratable):
    def elaborate(self, platform):

        leds12 = Cat([l for l in platform.request("leds12")])
        timer = Signal(38)

        m = Module()
        m.d.sync += timer.eq(timer + 1)
        m.d.comb += leds12.eq(timer[-15:-1])
        return m


class QSPIE2LedTestold(Elaboratable):
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

class QSPIE2LedTest(Elaboratable):
    def elaborate(self, platform):
        led_display = Cat([l for l in platform.request("leds12")])
        qd0 = platform.request("qd0").i
        qd1 = platform.request("qd1").i
        qd2 = platform.request("qd2").i
        qd3 = platform.request("qd3").i
        qck = Signal()
        qss = Signal()
        nibble = Signal(4)
        display = Signal(8)
        data = Signal(8)

        qdr = platform.request("qdr")

        m = Module()

        m.d.comb += [
            qck.eq(platform.request("qck")),
            qss.eq(platform.request("qss")),
            nibble.eq(Cat(qd0, qd1, qd2, qd3)),
            led_display.eq(Cat(display, Repl(C(0, 1), 4)))
        ]

        with m.If(qss):
            with m.If(Rose(qss)):
                m.d.sync += [
                    display.eq(data),
                    data.eq(0)
                ]
        with m.Else():
            with m.If(Rose(qck)):
                m.d.sync += [
                    data.eq(Cat(nibble, data[:-4]))
                ]

        return m

def synth():
    platform = IceLogicBusPlatform()
    platform.add_resources(leds12_tile)
    # platform.build(LEDTileTest(), do_program=True)
    platform.build(QSPIE2LedTest(), do_program=True)

if __name__ == "__main__":
    platform = IceLogicDeckPlatform()
    platform.add_resources(leds12_tile)
    # platform.build(LEDTileTest(), do_program=True)
    platform.build(LEDTileTest(), do_program=True)
