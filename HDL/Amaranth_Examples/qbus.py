from amaranth import *
from amaranth.hdl.ast import Rose
from amaranth.utils import bits_for

from mystorm_boards.icelogicbus import *
from HDL.Tiles import SevenSegController, tile_resources

TILE = 1

class SpiMem(Elaboratable):
    def __init__(self, addr_bits=32, data_bits=8):
        # parameters
        self.addr_bits = addr_bits  # Must be power of 2
        self.data_bits = data_bits  # currently must be 8

        # inputs
        self.copi = Signal()
        self.din = Signal(data_bits)
        self.csn = Signal()
        self.sclk = Signal()

        # outputs
        self.addr = Signal(addr_bits)
        self.cipo = Signal()
        self.dout = Signal(data_bits)
        self.rd = Signal()
        self.wr = Signal()

    def elaborate(self, platform):
        m = Module()

        r_req_read = Signal()
        r_req_write = Signal()
        r_data = Signal(self.data_bits)
        r_addr = Signal(self.addr_bits + 1)

        r_bit_count = Signal(bits_for(self.addr_bits + 8) + 1)

        r_copi = Signal()
        r_sclk = Signal(2)

        # Drive outputs
        m.d.comb += [
            self.rd.eq(r_req_read),
            self.wr.eq(r_req_write),
            self.cipo.eq(r_data[-1]),
            self.dout.eq(r_data),
            self.addr.eq(r_addr[:-1])
        ]

        # De-glitch and edge detection
        m.d.sync += [
            r_copi.eq(self.copi),
            r_sclk.eq(Cat(self.sclk, r_sclk[:-1]))
        ]

        # State machine
        with m.If(self.csn):
            m.d.sync += [
                r_req_read.eq(0),
                r_req_write.eq(0),
                r_bit_count.eq(self.addr_bits + 7)
            ]
        with m.Else():  # csn == 0
            with m.If(r_sclk == 0b01):  # rising sclk
                # If writing shift in data
                m.d.sync += r_data.eq(Mux(r_req_read, self.din, Cat(r_copi, r_data[:-1])))
                with m.If(r_bit_count[-1] == 0):  # Address bits
                    m.d.sync += [
                        r_bit_count.eq(r_bit_count - 1),
                        r_addr.eq(Cat(r_copi, r_addr[:-1]))  # Shift in address
                    ]
                with m.Else():  # read or write
                    with m.If(r_bit_count[:4] == 7):  # First bit in new byte, increment address
                        m.d.sync += r_addr[:-1].eq(r_addr[:-1] + 1)
                    m.d.sync += r_req_read.eq(Mux(r_bit_count[:3] == 1, r_addr[-1], 0))
                    with m.If(r_bit_count[:3] == 0):  # Last bit in byte
                        with m.If(r_addr[-1] == 0):
                            m.d.sync += r_req_write.eq(1)
                        m.d.sync += r_bit_count[3].eq(0)  # Allow increment of address
                    with m.Else():
                        m.d.sync += r_req_write.eq(0)
                    m.d.sync += r_bit_count[:3].eq(r_bit_count[:3] - 1)

        return m

class QspiMem(Elaboratable):
    def __init__(self, addr_bits=32, data_bits=16):
        # parameters
        self.addr_bits = addr_bits  # Must be power of 2
        self.data_bits = data_bits  # currently must be 8
        self.addr_nibbles = 2*addr_bits
        self.data_nibbles = 2*data_bits

        # inputs
        self.copi = Signal(4)
        self.din = Signal(data_bits)
        self.csn = Signal()
        self.sclk = Signal()

        # outputs
        self.addr = Signal(addr_bits + 7)
        self.cipo = Signal(4)
        self.dout = Signal(data_bits)
        self.rd = Signal()
        self.wr = Signal()

    def elaborate(self, platform):
        m = Module()

        r_req_read = Signal()
        r_req_write = Signal()
        r_cmd = Signal(self.data_bits)
        r_data = Signal(self.data_bits)
        r_addr = Signal(self.addr_bits + 7)

        r_nibble_count = Signal(bits_for(12))

        r_copi = Signal(4)
        r_sclk = Signal() # use ffsync

        # Drive outputs
        m.d.comb += [
            self.rd.eq(r_req_read),
            self.wr.eq(r_req_write),
            self.cipo.eq(r_data[-4]),
            self.dout.eq(r_data),
            self.addr.eq(r_addr),
        ]

        # De-glitch and edge detection
        m.d.sync += [
            r_copi.eq(self.copi),
            r_sclk.eq(self.sclk)
            #r_sclk.eq(Cat(self.sclk, r_sclk[:-1]))
        ]

        with m.If(self.csn):
            m.d.sync += [
                r_req_read.eq(0),
                r_req_write.eq(0),
                r_nibble_count.eq(0)
            ]
        with m.Else():  # csn == 0
            with m.If(Rose(r_sclk)):
                r_nibble_count.eq(r_nibble_count + 1)
                m.d.sync += r_data.eq(Mux(r_req_read, self.din, Cat(r_copi, r_data[:-4])))
                with m.FSM():
                    with m.State("COMMAND"):
                        m.d.sync += r_cmd.eq(Cat(r_copi, r_cmd[:-4]))
                        with m.If(r_nibble_count == 2):
                            m.next = "ADDRESS"
                    with m.State("ADDRESS"):
                        with m.If(r_nibble_count == self.addr_nibbles+2):
                            m.d.sync += r_addr.eq(Cat(r_cmd[:7], r_copi, r_addr[:-11]))
                            m.next = "DATA"
                        with m.Else():
                            m.d.sync += r_addr.eq(Cat(r_copi, r_addr[:-4])),
                    with m.State("DATA"):
                        # write data
                        r_data.eq(Cat(r_copi, r_data[:-4]))
                        with m.If(r_nibble_count == self.addr_nibbles+2+self.data_nibbles):
                            m.d.sync += [
                                r_req_read.eq(0),
                                r_req_write.eq(~r_cmd[-1:]),
                                r_addr.eq(r_addr + 1),
                                r_nibble_count.eq(self.addr_nibbles+2)
                            ]
                        with m.Else():
                            m.d.sync += [
                                r_req_write.eq(0),
                                r_req_read.eq(r_cmd[-1:])
                            ]



class QbusTest(Elaboratable):
    def elaborate(self, platform):
        csn = platform.request("qss")
        sclk = platform.request("qck")
        copi = platform.request("qd0").i
        cipo = platform.request("qd1", dir="-")

        m = Module()

        rd = Signal()
        wr = Signal()
        addr = Signal(32)
        din = Signal(8)
        dout = Signal(8)
        flags = Signal(8)

        m.submodules.spimem = spimem = SpiMem()

        mem = Memory(width=8, depth=4 * 1024)
        m.submodules.r = r = mem.read_port()
        m.submodules.w = w = mem.write_port()

        m.d.comb += [
            spimem.csn.eq(csn),
            spimem.sclk.eq(sclk),
            spimem.copi.eq(copi),
            spimem.din.eq(din),
            cipo.eq(spimem.cipo),
            addr.eq(spimem.addr),
            dout.eq(spimem.dout),
            rd.eq(spimem.rd),
            wr.eq(spimem.wr),
            r.addr.eq(addr),
            din.eq(r.data),
            w.data.eq(dout),
            w.addr.eq(addr),
            w.en.eq(wr),
            flags.eq(Cat(C(0, 6), spimem.wr, spimem.rd))
        ]

        m.submodules.seven = seven = SevenSegController()
        display = Signal(8)

        # Get pins
        seg_pins = platform.request("seven_seg_tile")
        leds7 = Cat([seg_pins.a, seg_pins.b, seg_pins.c, seg_pins.d,
                     seg_pins.e, seg_pins.f, seg_pins.g])

        timer = Signal(20)
        m.d.sync += timer.eq(timer + 1)

        m.d.comb += [
            leds7.eq(seven.leds)
        ]

        for i in range(3):
            m.d.comb += seg_pins.ca[i].eq(timer[16:18] == i)

        with m.If(seg_pins.ca[2]):
            m.d.comb += seven.val.eq(1)
        with m.If(seg_pins.ca[1]):
            m.d.comb += seven.val.eq(display[-4:])
        with m.If(seg_pins.ca[0]):
            m.d.comb += seven.val.eq(display[:4])

        with m.If(spimem.wr): # & (spimem.addr == LED_ADDR)
            m.d.sync += display.eq(1)
            #m.d.sync += display.eq(spimem.dout)

        return m

def synth():
    platform = IceLogicBusPlatform()
    platform.add_resources(tile_resources(TILE))
    platform.build(QbusTest(), do_program=True)
    # platform.bus_send(bytearray(b'\x03\x00\x00\x00\x01\xdb'))