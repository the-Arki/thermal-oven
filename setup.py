import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import adafruit_max31865
from adafruit_character_lcd.character_lcd import Character_LCD_Mono


# setup Max_31865 sensor
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=board.GP12)
cs = DigitalInOut(board.GP13)
sensor = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=100, ref_resistor=430.0, wires=3)
temp_actual = sensor.temperature


# set lcd pins
lcd_rs = DigitalInOut(board.GP16)
lcd_en = DigitalInOut(board.GP17)
lcd_d4 = DigitalInOut(board.GP18)
lcd_d5 = DigitalInOut(board.GP19)
lcd_d6 = DigitalInOut(board.GP20)
lcd_d7 = DigitalInOut(board.GP21)

# set lcd size
lcd_columns = 16
lcd_rows = 2

# initialize lcd
lcd = Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

# setup button up
btn_up = DigitalInOut(board.GP22)
btn_up.direction = Direction.INPUT
btn_up.pull = Pull.DOWN

# setup button down
btn_down = DigitalInOut(board.GP26)
btn_down.direction = Direction.INPUT
btn_down.pull = Pull.DOWN

# setup relay
relay = DigitalInOut(board.GP6)
relay.direction = Direction.OUTPUT