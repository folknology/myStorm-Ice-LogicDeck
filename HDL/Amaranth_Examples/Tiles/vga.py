from typing import NamedTuple

from amaranth import *
from amaranth.build import *

# Abstracts the VGA Frame timing sections
class VGATiming(NamedTuple):
    x: int
    y: int
    refresh_rate: float
    pixel_freq: int
    h_front_porch: int
    h_sync_pulse: int
    h_back_porch: int
    v_front_porch: int
    v_sync_pulse: int
    v_back_porch: int


# Generates a VGA picture from sequential bitmap data from pixel clock
# synchronous FIFO.
#
# The pixel data in i_r, i_g, and i_b registers
# should be present ahead of time.
#
# Signal 'o_fetch_next' is set high for 1 'pixel' clock
# period as soon as current pixel data is consumed.
# The FIFO should be fast enough to fetch new data
# for the new pixel.
class VGADriver(Elaboratable):
    def __init__(self, timing: VGATiming,
                 bits_x            = 10, # should fit resolution_x + hsync_front_porch + hsync_pulse + hsync_back_porch
                 bits_y            = 10, # should fit resolution_y + vsync_front_porch + vsync_pulse + vsync_back_porch
                 ):
        # ClockEnable and Colour Pixel input signals
        self.i_clk_en       = Signal()
        self.i_r            = Signal(8)
        self.i_g            = Signal(8)
        self.i_b            = Signal(8)
        # Frame Buffer timing signals
        self.o_fetch_next   = Signal()
        self.o_beam_x       = Signal(bits_x)
        self.o_beam_y       = Signal(bits_y)
        # Output Blanking signals
        self.o_vga_vblank = Signal()
        self.o_vga_blank = Signal()
        self.o_vga_de = Signal()
        # Output signals for driving DAC/SYNC
        self.o_vga_r = Signal(8)
        self.o_vga_g = Signal(8)
        self.o_vga_b = Signal(8)
        self.o_vga_hsync = Signal()
        self.o_vga_vsync = Signal()
        # Timing constants
        self.timing = timing
        # Configuration
        self.bits_x = bits_x
        self.bits_y = bits_y

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # Constants
        C_hblank_on = C(self.timing.x - 1, unsigned(self.bits_x))
        C_hsync_on = C(self.timing.x + self.timing.h_front_porch - 1, unsigned(self.bits_x))
        C_hsync_off = C(self.timing.x + self.timing.h_front_porch + self.timing.h_sync_pulse - 1, unsigned(self.bits_x))
        C_hblank_off = C(self.timing.x + self.timing.h_front_porch + self.timing.h_sync_pulse + self.timing.h_back_porch - 1, unsigned(self.bits_x))
        C_frame_x = C_hblank_off
        # frame x = 640 + 16 + 96 + 48 = 800

        C_vblank_on = C(self.timing.y - 1, unsigned(self.bits_y))
        C_vsync_on = C(self.timing.y + self.timing.v_front_porch - 1, unsigned(self.bits_y))
        C_vsync_off = C(self.timing.y + self.timing.v_front_porch + self.timing.v_sync_pulse - 1, unsigned(self.bits_y))
        C_vblank_off = C(self.timing.y + self.timing.v_front_porch + self.timing.v_sync_pulse + self.timing.v_back_porch - 1, unsigned(self.bits_y))
        C_frame_y = C_vblank_off
        # frame y = 480 + 10 + 2 + 33 = 525
        # refresh rate = pixel clock / (frame x * frame y) = 25 MHz / (800 * 525) = 59.52 Hz

        # Internal signals
        R_hsync = Signal()
        R_vsync = Signal()
        R_disp = Signal() # disp == not blank
        R_disp_early = Signal()
        R_vdisp = Signal()
        R_blank_early = Signal()
        R_vblank = Signal()
        R_fetch_next = Signal()
        CounterX = Signal(self.bits_x)
        CounterY = Signal(self.bits_y)
        R_blank = Signal()

        with m.If(self.i_clk_en):
            with m.If(CounterX == C_frame_x):
                m.d.pixel += CounterX.eq(0)

                with m.If(CounterY == C_frame_y):
                    m.d.pixel += CounterY.eq(0)
                with m.Else():
                    m.d.pixel += CounterY.eq(CounterY + 1)
            with m.Else():
                m.d.pixel += CounterX.eq(CounterX + 1)

            m.d.pixel += R_fetch_next.eq(R_disp_early)
        with m.Else():
            m.d.pixel += R_fetch_next.eq(0)

        m.d.comb += [
            self.o_beam_x.eq(CounterX),
            self.o_beam_y.eq(CounterY),
            self.o_fetch_next.eq(R_fetch_next),
        ]

        # Generate sync and blank.
        with m.If(CounterX == C_hblank_on):
            m.d.pixel += [
                R_blank_early.eq(1),
                R_disp_early.eq(0)
            ]
        with m.Elif(CounterX == C_hblank_off):
            m.d.pixel += [
                R_blank_early.eq(R_vblank),
                R_disp_early.eq(R_vdisp)
            ]
        with m.If(CounterX == C_hsync_on):
            m.d.pixel += R_hsync.eq(1)
        with m.Elif(CounterX == C_hsync_off):
            m.d.pixel += R_hsync.eq(0)

        with m.If(CounterY == C_vblank_on):
            m.d.pixel += [
                R_vblank.eq(1),
                R_vdisp.eq(0)
            ]
        with m.Elif(CounterY == C_vblank_off):
            m.d.pixel += [
                R_vblank.eq(0),
                R_vdisp.eq(1)
            ]
        with m.If(CounterY == C_vsync_on):
            m.d.pixel += R_vsync.eq(1)
        with m.Elif(CounterY == C_vsync_off):
            m.d.pixel += R_vsync.eq(0)

        m.d.pixel += R_blank.eq(R_blank_early)
        m.d.pixel += R_disp.eq(R_disp_early)

        m.d.comb += [
            self.o_vga_r.eq(self.i_r),
            self.o_vga_g.eq(self.i_g),
            self.o_vga_b.eq(self.i_b),
            self.o_vga_hsync.eq(R_hsync),
            self.o_vga_vsync.eq(R_vsync),
            self.o_vga_blank.eq(R_blank),
            self.o_vga_de.eq(R_disp),
        ]

        return m

# Generates a VGA Test Pattern
class VGATestPattern(Elaboratable):
    def __init__(self, vga: VGADriver):
        self.vga = vga

    def elaborate(self, platform: Platform) -> Module:
        W = Signal(8)
        A = Signal(8)
        T = Signal(8)
        Z = Signal(6)
        m = Module()

        # Test pattern fundamentals
        m.d.comb += [
            A.eq(Mux(
                (self.vga.o_beam_x[5:8] == 0b010) & (self.vga.o_beam_y[5:8] == 0b010),
                0xFF, 0)),
            W.eq(Mux(
                (self.vga.o_beam_x[:8] == self.vga.o_beam_y[:8]),
                0xFF, 0)),
            Z.eq(Mux(
                (self.vga.o_beam_y[3:5] == ~(self.vga.o_beam_x[3:5])),
                0xFF, 0)),
            T.eq(Repl(self.vga.o_beam_y[6], len(T))),
        ]

        # Mux Emit rgb test pattern pixels unless within blanking period
        with m.If(self.vga.o_vga_blank):
            m.d.pixel += [
                self.vga.i_r.eq(0),
                self.vga.i_g.eq(0),
                self.vga.i_b.eq(0),
            ]
        with m.Else():
            m.d.pixel += [
                self.vga.i_r.eq((Cat(0b00, self.vga.o_beam_x[:6] & Z) | W) & (~A)),
                self.vga.i_g.eq(((self.vga.o_beam_x[:8] & T) | W) & (~A)),
                self.vga.i_b.eq(self.vga.o_beam_x[:8] | W | A),
            ]

        return m

vga_timings = {
     '640x350@70Hz': VGATiming(
        x             = 640,
        y             = 350,
        refresh_rate  = 70.0,
        pixel_freq    = 25_175_000,
        h_front_porch = 16,
        h_sync_pulse  = 96,
        h_back_porch  = 48,
        v_front_porch = 37,
        v_sync_pulse  = 2,
        v_back_porch  = 60),
    '640x350@85Hz': VGATiming(
        x             = 640,
        y             = 350,
        refresh_rate  = 85.0,
        pixel_freq    = 31_500_000,
        h_front_porch = 32,
        h_sync_pulse  = 64,
        h_back_porch  = 96,
        v_front_porch = 32,
        v_sync_pulse  = 3,
        v_back_porch  = 60),
    '640x400@70Hz': VGATiming(
        x             = 640,
        y             = 400,
        refresh_rate  = 70.0,
        pixel_freq    = 25_175_000,
        h_front_porch = 16,
        h_sync_pulse  = 96,
        h_back_porch  = 48,
        v_front_porch = 12,
        v_sync_pulse  = 2,
        v_back_porch  = 35),
    '640x400@85Hz': VGATiming(
        x             = 640,
        y             = 400,
        refresh_rate  = 85.0,
        pixel_freq    = 31_500_000,
        h_front_porch = 32,
        h_sync_pulse  = 64,
        h_back_porch  = 96,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 41),
    '640x480@60Hz': VGATiming(
        x             = 640,
        y             = 480,
        refresh_rate  = 60.0,
        pixel_freq    = 25_175_000,
        h_front_porch = 16,
        h_sync_pulse  = 96,
        h_back_porch  = 48,
        v_front_porch = 10,
        v_sync_pulse  = 2,
        v_back_porch  = 33),
    '720x400@85Hz': VGATiming(
        x             = 720,
        y             = 400,
        refresh_rate  = 85.0,
        pixel_freq    = 35_500_000,
        h_front_porch = 36,
        h_sync_pulse  = 72,
        h_back_porch  = 108,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 42),
    '768x576@60Hz': VGATiming(
        x             = 758,
        y             = 576,
        refresh_rate  = 60.0,
        pixel_freq    = 34_960_000,
        h_front_porch = 24,
        h_sync_pulse  = 80,
        h_back_porch  = 104,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 17),
    '768x576@72Hz': VGATiming(
        x             = 758,
        y             = 576,
        refresh_rate  = 72.0,
        pixel_freq    = 42_930_000,
        h_front_porch = 32,
        h_sync_pulse  = 80,
        h_back_porch  = 112,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 21),
    '768x576@75Hz': VGATiming(
        x             = 758,
        y             = 576,
        refresh_rate  = 75.0,
        pixel_freq    = 45_510_000,
        h_front_porch = 40,
        h_sync_pulse  = 80,
        h_back_porch  = 120,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 22),
    '800x600@60Hz': VGATiming(
        x             = 800,
        y             = 600,
        refresh_rate  = 60.0,
        pixel_freq    = 40_000_000,
        h_front_porch = 40,
        h_sync_pulse  = 128,
        h_back_porch  = 88,
        v_front_porch = 1,
        v_sync_pulse  = 4,
        v_back_porch  = 23),
    '848x480@60Hz': VGATiming(
        x             = 848,
        y             = 480,
        refresh_rate  = 60.0,
        pixel_freq    = 33_750_000,
        h_front_porch = 16,
        h_sync_pulse  = 112,
        h_back_porch  = 112,
        v_front_porch = 6,
        v_sync_pulse  = 8,
        v_back_porch  = 23),
    '1024x768@60Hz': VGATiming(
        x             = 1024,
        y             = 768,
        refresh_rate  = 60.0,
        pixel_freq    = 65_000_000,
        h_front_porch = 24,
        h_sync_pulse  = 136,
        h_back_porch  = 160,
        v_front_porch = 3,
        v_sync_pulse  = 6,
        v_back_porch  = 29),
    '1152x864@60Hz': VGATiming(
        x             = 1152,
        y             = 864,
        refresh_rate  = 60.0,
        pixel_freq    = 81_620_000,
        h_front_porch = 64,
        h_sync_pulse  = 120,
        h_back_porch  = 184,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 27),
    '1280x720@60Hz': VGATiming(
        x             = 1280,
        y             = 720,
        refresh_rate  = 60.0,
        pixel_freq    = 74_250_000,
        h_front_porch = 110,
        h_sync_pulse  = 40,
        h_back_porch  = 220,
        v_front_porch = 5,
        v_sync_pulse  = 5,
        v_back_porch  = 20),
    '1280x768@60Hz': VGATiming(
        x             = 1280,
        y             = 768,
        refresh_rate  = 60.0,
        pixel_freq    = 79_500_000,
        h_front_porch = 64,
        h_sync_pulse  = 128,
        h_back_porch  = 192,
        v_front_porch = 3,
        v_sync_pulse  = 7,
        v_back_porch  = 20),
    '1280x768@60Hz CVT-RB': VGATiming(
        x             = 1280,
        y             = 768,
        refresh_rate  = 60.0,
        pixel_freq    = 68_250_000,
        h_front_porch = 48,
        h_sync_pulse  = 32,
        h_back_porch  = 80,
        v_front_porch = 3,
        v_sync_pulse  = 7,
        v_back_porch  = 12),
    '1280x800@60Hz': VGATiming(
        x             = 1280,
        y             = 800,
        refresh_rate  = 60.0,
        pixel_freq    = 83_500_000,
        h_front_porch = 72,
        h_sync_pulse  = 128,
        h_back_porch  = 200,
        v_front_porch = 3,
        v_sync_pulse  = 6,
        v_back_porch  = 22),
    '1280x800@60Hz CVT-RB': VGATiming(
        x             = 1280,
        y             = 800,
        refresh_rate  = 60.0,
        pixel_freq    = 71_000_000,
        h_front_porch = 48,
        h_sync_pulse  = 32,
        h_back_porch  = 80,
        v_front_porch = 3,
        v_sync_pulse  = 6,
        v_back_porch  = 14),
    '1280x1024@60Hz': VGATiming(
        x             = 1280,
        y             = 1024,
        refresh_rate  = 60.0,
        pixel_freq    = 108e6,
        h_front_porch = 48,
        h_sync_pulse  = 112,
        h_back_porch  = 248,
        v_front_porch = 1,
        v_sync_pulse  = 3,
        v_back_porch  = 38),
    '1366x768@60Hz': VGATiming(
        x             = 1366,
        y             = 768,
        refresh_rate  = 60.0,
        pixel_freq    = 85_500_000,
        h_front_porch = 70,
        h_sync_pulse  = 143,
        h_back_porch  = 213,
        v_front_porch = 3,
        v_sync_pulse  = 3,
        v_back_porch  = 24),
    '1920x1080@30Hz': VGATiming(
        x             = 1920,
        y             = 1080,
        refresh_rate  = 30.0,
        pixel_freq    = 148_500_000//2,
        h_front_porch = 88,
        h_sync_pulse  = 44,
        h_back_porch  = 148,
        v_front_porch = 4,
        v_sync_pulse  = 5,
        v_back_porch  = 36),
    '1920x1080@30Hz CVT-RB': VGATiming(
        x             = 1920,
        y             = 1080,
        refresh_rate  = 30.0,
        pixel_freq    = 73_000_000,
        h_front_porch = 48,
        h_sync_pulse  = 32,
        h_back_porch  = 80,
        v_front_porch = 3,
        v_sync_pulse  = 5,
        v_back_porch  = 9),
    '1920x1080@30Hz CVT-RB2': VGATiming(
        x             = 1920,
        y             = 1080,
        refresh_rate  = 30.0,
        pixel_freq    = 70_208_000,
        h_front_porch = 8,
        h_sync_pulse  = 32,
        h_back_porch  = 40,
        v_front_porch = 3,
        v_sync_pulse  = 8,
        v_back_porch  = 6),
    '1920x1080@60Hz': VGATiming(
        x             = 1920,
        y             = 1080,
        refresh_rate  = 60.0,
        pixel_freq    = 148_500_000,
        h_front_porch = 88,
        h_sync_pulse  = 44,
        h_back_porch  = 148,
        v_front_porch = 4,
        v_sync_pulse  = 5,
        v_back_porch  = 36),
}
