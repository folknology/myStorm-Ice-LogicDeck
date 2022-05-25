from amaranth import *
from amaranth.hdl.ast import Rose

from mystorm_boards.icelogicbus import *
from HDL.Tiles.seven_seg_tile import SevenSegController, tile_resources

TILE = 3

class SevenSegExampleOld(Elaboratable):
    def elaborate(self, platform):
        # Add 7-segment controller
        m = Module()
        m.submodules.seven = seven = SevenSegController()

        # Get pins
        seg_pins = platform.request("seven_seg_tile")
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d,
                     seg_pins.e, seg_pins.f, seg_pins.g])

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


class SevenSegExample(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.seven = seven = SevenSegController()

        seg_pins = platform.request("seven_seg_tile")
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d, seg_pins.e, seg_pins.f, seg_pins.g])
        timer = Signal(40)
        m.d.sync += timer.eq(timer + 1)

        m.d.comb += [
            leds7.eq(seven.leds)
        ]
        for i in range(3):
            m.d.comb += seg_pins.ca[i].eq(timer[17:19] == i)
            with m.If(seg_pins.ca[i]):
                m.d.comb += seven.val.eq(timer[((i - 3) * 4) - 5:((i - 3) * 4) - 1])

        return m

class QSPIE2SevenSegExample(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.seven = seven = SevenSegController()

        seg_pins = platform.request("seven_seg_tile")
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d, seg_pins.e, seg_pins.f, seg_pins.g])

        qd0 = platform.request("qd0").i
        qd1 = platform.request("qd1").i
        qd2 = platform.request("qd2").i
        qd3 = platform.request("qd3").i
        qck = Signal()
        qss = Signal()
        nibble = Signal(4)
        display = Signal(8)
        data = Signal(13)

        qdr = platform.request("qdr")

        timer = Signal(20)
        m.d.sync += timer.eq(timer + 1)

        m.d.comb += [
            leds7.eq(seven.leds)
        ]

        for i in range(3):
            m.d.comb += seg_pins.ca[i].eq(timer[16:18] == i)
            # with m.If(seg_pins.ca[i]):
            #     m.d.comb += seven.val.eq(display[((i - 3) * 3) - 5:((i - 3) * 3) - 1])

        with m.If(seg_pins.ca[1]):
            m.d.comb += seven.val.eq(display[-4:])
        with m.If(seg_pins.ca[0]):
            m.d.comb += seven.val.eq(display[-8:-4])

        m.d.comb += [
            qck.eq(platform.request("qck")),
            qss.eq(platform.request("qss")),
            nibble.eq(Cat(qd0, qd1, qd2, qd3)),
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
    platform.add_resources(tile_resources(TILE))
    #platform.build(QSPIE2SevenSegExample(), do_program=True)
    platform.build(SevenSegExample(), do_program=True)
    # platform.bus_send(bytearray(b'\x00\xff'))


if __name__ == "__main__":
    platform = IceLogicBusPlatform()
    platform.add_resources(tile_resources(TILE))
    platform.build(SevenSegExample(), do_program=True)