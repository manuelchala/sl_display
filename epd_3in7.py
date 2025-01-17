# -----------------------------------------------------------------------------
# Author               :   Coen Tempelaars
# Original author      :   Waveshare team
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from machine import Pin, SPI
import framebuf
import time

# Display resolution
EPD_WIDTH       = 280
EPD_WIDTH_BYTES = 35
EPD_HEIGHT      = 480

# Canvas resolution (landscape orientation)
CANVAS_WIDTH    = EPD_HEIGHT
CANVAS_HEIGHT   = EPD_WIDTH

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

EPD_3IN7_lut_1Gray_GC =[
0x2A,0x05,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x05,0x2A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x2A,0x15,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x05,0x0A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x02,0x03,0x0A,0x00,0x02,0x06,0x0A,0x05,0x00,#6
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]

class EPD_3in7(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)

        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)

        self.black = 0x00
        self.white = 0xff
        self.darkgray = 0xaa
        self.grayish = 0x55

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.width = CANVAS_WIDTH
        self.height = CANVAS_HEIGHT
        self.buffer = bytearray(EPD_HEIGHT * EPD_WIDTH_BYTES)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

        self.init()
        self.clear()
        time.sleep_ms(500)

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        time.sleep_ms(30)
        self.digital_write(self.reset_pin, 0)
        time.sleep_ms(30)
        self.digital_write(self.reset_pin, 1)
        time.sleep_ms(30)

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def wait_until_idle(self):
        while(self.digital_read(self.busy_pin) == 1):
            time.sleep_ms(10)
        time.sleep_ms(200)

    def load_lut(self):
        self.send_command(0x32)
        for count in range(0, 105):
            self.send_data(EPD_3IN7_lut_1Gray_GC[count])

    def deep_sleep(self):
        time.sleep_ms(500)
        self.send_command(0X50)
        self.send_data(0xf7)
        self.send_command(0X02)  # power off
        self.send_command(0X07)  # deep sleep
        self.send_data(0xA5)

    def init(self):
        self.reset()

        self.send_command(0x12)
        time.sleep_ms(300)

        self.send_command(0x46)
        self.send_data(0xF7)
        self.wait_until_idle()
        self.send_command(0x47)
        self.send_data(0xF7)
        self.wait_until_idle()

        self.send_command(0x01)   # setting gaet number
        self.send_data(0xDF)
        self.send_data(0x01)
        self.send_data(0x00)

        self.send_command(0x03)   # set gate voltage
        self.send_data(0x00)

        self.send_command(0x04)   # set source voltage
        self.send_data(0x41)
        self.send_data(0xA8)
        self.send_data(0x32)

        self.send_command(0x11)   # set data entry sequence
        self.send_data(0x03)

        self.send_command(0x3C)   # set border
        self.send_data(0x03)

        self.send_command(0x0C)   # set booster strength
        self.send_data(0xAE)
        self.send_data(0xC7)
        self.send_data(0xC3)
        self.send_data(0xC0)
        self.send_data(0xC0)

        self.send_command(0x18)   # set internal sensor on
        self.send_data(0x80)

        self.send_command(0x2C)   # set vcom value
        self.send_data(0x44)

        self.send_command(0x37)   # set display option, these setting turn on previous function
        self.send_data(0x00)      # can switch 1 gray or 4 gray
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0x4F)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)
        self.send_data(0xFF)

        self.send_command(0x44)   # setting X direction start/end position of RAM
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x17)
        self.send_data(0x01)

        self.send_command(0x45)   # setting Y direction start/end position of RAM
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0xDF)
        self.send_data(0x01)

        self.send_command(0x22)   # Display Update Control 2
        self.send_data(0xCF)

    def clear(self):
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x24)
        for j in range(0, EPD_HEIGHT):
            for i in range(0, EPD_WIDTH_BYTES):
                self.send_data(0Xff)

        self.load_lut()

        self.send_command(0x20)
        self.wait_until_idle()

    def show(self):
        epd_buffer = bytearray(EPD_HEIGHT * EPD_WIDTH_BYTES)

        # Rotate self.buffer (a canvas in landscape orientation)
        # and copy it into epd_buffer which is sent to the Pico
        x=0; y=0; n=1; R=0
        for i in range(1, EPD_WIDTH_BYTES+1):
            for j in range(1, EPD_HEIGHT+1):
                R = (n-x)+((n-y)*(EPD_WIDTH_BYTES-1))
                epd_buffer[R-1] = self.buffer[n-1]
                n += 1
            x = n+i-1
            y = n-1

        self.send_command(0x49)
        self.send_data(0x00)

        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x24)
        for j in range(0, EPD_HEIGHT):
            for i in range(0, EPD_WIDTH_BYTES):
                self.send_data(epd_buffer[i + j * EPD_WIDTH_BYTES])

        self.load_lut()

        self.send_command(0x20)
        self.wait_until_idle()
