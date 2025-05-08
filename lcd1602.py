from machine import I2C
import time

class LCD1602(object):
    # Commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, i2c, lines=2, dotsize=0, lcd_addr=0x3E):
        self.i2c = i2c
        self.lcd_address = lcd_addr
        self.line = lines
        self.currline = 0

        time.sleep_ms(50)

        function_set = self.LCD_FUNCTIONSET | self.LCD_4BITMODE
        if lines > 1:
            function_set |= self.LCD_2LINE
        if dotsize != 0 and lines == 1:  # it was if (dotsize != 0 & lines == 1):
            function_set |= self.LCD_5x10DOTS
        else:
            function_set |= self.LCD_5x8DOTS

        self.command(function_set)
        time.sleep_us(4500)
        self.command(function_set)
        time.sleep_us(150)
        self.command(function_set)

        # Display on, cursor off, blink off
        self.display_control = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display()

        # Clear display
        self.clear()

        # Entry mode
        self.display_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.command(self.LCD_ENTRYMODESET | self.display_mode)

    def clear(self):
        self.command(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2)

    def home(self):
        self.command(self.LCD_RETURNHOME)
        time.sleep_ms(2)

    def setCursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.line:
            row = self.line - 1
        self.command(self.LCD_SETDDRAMADDR | (col + row_offsets[row]))

    def no_display(self):
        self.display_control &= ~self.LCD_DISPLAYON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def display(self):
        self.display_control |= self.LCD_DISPLAYON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def no_cursor(self):
        self.display_control &= ~self.LCD_CURSORON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def cursor(self):
        self.display_control |= self.LCD_CURSORON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def no_blink(self):
        self.display_control &= ~self.LCD_BLINKON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def blink(self):
        self.display_control |= self.LCD_BLINKON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def autoscroll(self):
        self.display_mode |= self.LCD_ENTRYSHIFTINCREMENT
        self.command(self.LCD_ENTRYMODESET | self.display_mode)

    def no_autoscroll(self):
        self.display_mode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.command(self.LCD_ENTRYMODESET | self.display_mode)

    def create_char(self, location, charmap):
        location &= 0x7
        self.command(self.LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self.write(charmap[i])

    def command(self, command):
        self.i2c.writeto_mem(self.lcd_address, 0x80, bytearray([command]))

    def write(self, data):
        self.i2c.writeto_mem(self.lcd_address, 0x40, bytearray([data]))

    def print(self, text):
        for char in text:
            self.write(ord(char))


class LCD1602_RGB(LCD1602):
    WHITE = 0
    RED = 1
    GREEN = 2
    BLUE = 3

    REG_RED = 0x04
    REG_GREEN = 0x03
    REG_BLUE = 0x02

    def __init__(self, i2c, lines=2, dotsize=0, lcd_addr=0x3E, rgb_addr=0x62):
        self.rgb_address = rgb_addr
        super().__init__(i2c, lines, dotsize, lcd_addr)

        self.set_reg(0, 0)
        self.set_reg(1, 0)
        self.set_reg(0x08, 0xAA)
        self.set_rgb(255, 255, 255)

    def set_reg(self, addr, value):
        self.i2c.writeto_mem(self.rgb_address, addr, bytearray([value]))

    def set_rgb(self, r, g, b):
        self.set_reg(self.REG_RED, r)
        self.set_reg(self.REG_GREEN, g)
        self.set_reg(self.REG_BLUE, b)

    def set_color(self, color):
        if color == self.WHITE:
            self.set_rgb(255, 255, 255)
        elif color == self.RED:
            self.set_rgb(255, 0, 0)
        elif color == self.GREEN:
            self.set_rgb(0, 255, 0)
        elif color == self.BLUE:
            self.set_rgb(0, 0, 255)
