from amaranth import *
from IceLogicDeck import *
from Tiles.seven_seg_tile import SevenSegController, tile_resources

TILE = 1


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

from amaranth import *
from mystorm_boards.icelogicbus import *
from HDL.Amaranth_Examples.Tiles.seven_seg_tile import SevenSegController, tile_resources

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

def synth():
    platform = IceLogicBusPlatform()
    platform.add_resources(tile_resources(TILE))
    platform.build(SevenSegExample(), do_program=True)

if __name__ == "__main__":
    platform = IceLogicDeckPlatform()
    platform.add_resources(tile_resources(TILE))
    platform.build(SevenSegExample(), do_program=True)