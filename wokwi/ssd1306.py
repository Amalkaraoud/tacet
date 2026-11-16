"""Compact SSD1306 I2C driver (128x64 / 128x32) built on ``framebuf``.

Interface-compatible with the driver used in the course (chapter 4 / TP3):
``SSD1306_I2C(width, height, i2c, addr=0x3C)``, then ``fill``, ``text``,
``pixel``, ``show``. Written from the public SSD1306 datasheet command set.
"""
import framebuf

_SET_CONTRAST = 0x81
_SET_ENTIRE_ON = 0xA4
_SET_NORM_INV = 0xA6
_SET_DISP = 0xAE
_SET_MEM_ADDR = 0x20
_SET_COL_ADDR = 0x21
_SET_PAGE_ADDR = 0x22
_SET_DISP_START_LINE = 0x40
_SET_SEG_REMAP = 0xA0
_SET_MUX_RATIO = 0xA8
_SET_COM_OUT_DIR = 0xC0
_SET_DISP_OFFSET = 0xD3
_SET_COM_PIN_CFG = 0xDA
_SET_DISP_CLK_DIV = 0xD5
_SET_PRECHARGE = 0xD9
_SET_VCOM_DESEL = 0xDB
_SET_CHARGE_PUMP = 0x8D


class SSD1306_I2C(framebuf.FrameBuffer):
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        super().__init__(self.buffer, width, height, framebuf.MONO_VLSB)
        self._init_display()

    def _cmd(self, c):
        self.i2c.writeto(self.addr, bytes([0x80, c]))

    def _init_display(self):
        for c in (
            _SET_DISP, _SET_MEM_ADDR, 0x00,
            _SET_DISP_START_LINE, _SET_SEG_REMAP | 0x01,
            _SET_MUX_RATIO, self.height - 1,
            _SET_COM_OUT_DIR | 0x08, _SET_DISP_OFFSET, 0x00,
            _SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            _SET_DISP_CLK_DIV, 0x80, _SET_PRECHARGE, 0xF1,
            _SET_VCOM_DESEL, 0x30, _SET_CONTRAST, 0xFF,
            _SET_ENTIRE_ON, _SET_NORM_INV, _SET_CHARGE_PUMP, 0x14,
            _SET_DISP | 0x01,
        ):
            self._cmd(c)
        self.fill(0)
        self.show()

    def show(self):
        for c in (_SET_COL_ADDR, 0, self.width - 1, _SET_PAGE_ADDR, 0, self.pages - 1):
            self._cmd(c)
        self.i2c.writeto(self.addr, b"\x40" + self.buffer)
