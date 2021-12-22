import os
import subprocess

from amaranth.build import *
from amaranth_boards.resources import *
from amaranth.vendor.lattice_ice40 import LatticeICE40Platform

__all__ = ["IceLogicDeckPlatform"]

# Pinout definitions
LED =" D10" #B7
UART = " J2 K2" #Rx,Tx
SPI =" K9 J9 L10 L7" #si,so, sck,ss
USER = " J11 B6 D7 B7"
SUPER = " B4 A4 A1 B3 _ _ _ _"
GENPINS = " - - - - - - - -"
QSPIE = " J8 H7 K7 L8 H9 L7 J7" # qdo,qd1,qd2,qd3,qck,qss,qdr
TILE1 = " B1 B2 C4 C3 C2 C1 E1 D1 D2 D3 E2 E3"
TILE2 = " D10 D11 B11 C11 A10 A11 C9 B9 A7 B8 D5 B5"
TILE3 = " A9 C8 A8 C7 A6 A5 A2 A3 F11 E9 E10 E8"
TILE4 = " F1 F2 F4 F3 G1 G2 G3 H3 H1 H2 J1 K1"
TILE5 = " K11 H10 J10 G8 H11 G10 D9 E11 G9 G11 F10 F9"
MEZZA = UART + " - - - - - - - - - - - - - - - - - - - - - -"
MEZZB = USER + " - - - - - - - - - - - - - - - - - - - -"

# IceLogicDeck : https://github.com/folknology/IceLogicDeck
class IceLogicDeckPlatform(LatticeICE40Platform):
    device = "iCE40HX4K"
    package = "BG121"
    default_clk = "clk25"
    resources = [
        Resource("clk25", 0, Pins("L5", dir="i"),
                 Clock(25e6), Attrs(GLOBAL=True, IO_STANDARD="SB_LVCMOS")
                 ),
        # led
        Resource("led", 0, Pins(LED, dir="o", invert=True),
                 Attrs(IO_STANDARD="SB_LVCMOS")

                 ),
        # SPI
        Resource("sck", 0, Pins("L10", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("copi", 0, Pins("J9", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("cs_n", 0, Pins("L7", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("cipo", 0, Pins("K9", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # QSPIE
        Resource("qd0", 0, Pins("J8",  dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qd1", 0, Pins("H7",  dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qd2", 0, Pins("K7",  dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qd3", 0, Pins("l8",  dir="io"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qck", 0, Pins("H9", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qss", 0, Pins("L7", dir="i"), Attrs(IO_STANDARD="SB_LVCMOS")),
        Resource("qdr", 0, Pins("J7", dir="o"), Attrs(IO_STANDARD="SB_LVCMOS")),
        # Uart
        UARTResource(0,
                     rx="J2", tx="K2",
                     attrs=Attrs(IO_STANDARD="SB_LVCMOS", PULLUP=1),
                     role="dce"
                     ),
        *SPIFlashResources(0,
                           cs_n="L7", clk="L10", copi="J9", cipo="K9",
                           attrs=Attrs(IO_STANDARD="SB_LVCMOS")
                           )
        #Hyperram ?
    ]
    connectors  = [
        # Tile connectors
        Connector("tile", 1, TILE1 + GENPINS),  #
        Connector("tile", 2, TILE2 + SUPER),  #
        Connector("tile", 3, TILE3 + GENPINS),  #
        Connector("tile", 4, TILE4 + GENPINS),  #
        Connector("tile", 5, TILE5 + GENPINS),  #
        # Mezzanine Connectors
        Connector("mez", 0, MEZZA),  #
        Connector("mez", 1, MEZZB),  #
    ]

    def toolchain_program(self, products, name, **kwargs):
        device = os.environ.get("DEVICE", "/dev/ttyS6")
        print("Programming ", device)
        with products.extract("{}.bin".format(name)) as bitstream_filename:
            subprocess.check_call(["cp", bitstream_filename, device])


if __name__ == "__main__":
    #from .test.blinky import *
    from amaranth_boards.test.blinky import *
    IceLogicDeckPlatform().build(Blinky(), do_program=True)
