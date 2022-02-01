import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import time
import adafruit_max31865
from adafruit_character_lcd.character_lcd import Character_LCD_Mono
import math
from evaluate_temperature import Temperature
from control import ControlTemperature

# setup Max_31865 sensor
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=board.GP12)
cs = DigitalInOut(board.GP13)
sensor = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=100, ref_resistor=430.0, wires=3)
temp_actual = sensor.temperature

# set initial required temperature
with open("/temp.txt", "r") as t:
    temp_set = int(t.read())
print("initial temp_set: ", temp_set)

# initialize Temperature class
t = Temperature(temp_actual)
control = ControlTemperature(temp_set)

led = DigitalInOut(board.LED)
led.switch_to_output()
led.value = True
time.sleep(1)
led.value = False

#setup log pin
log_pin = DigitalInOut(board.GP0)
log_pin.direction = Direction.INPUT
log_pin.pull = Pull.UP
if log_pin.value:
    log_enabled = True
else:
    log_enabled = False

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

lcd.clear()
lcd.message = "Temp: {0:0.1f} C\nSet: {1:0.0f}".format(temp_actual, temp_set)

# setup button up
btn_up = DigitalInOut(board.GP22)
btn_up.direction = Direction.INPUT
btn_up.pull = Pull.DOWN

# setup button down
btn_down = DigitalInOut(board.GP26)
btn_down.direction = Direction.INPUT
btn_down.pull = Pull.DOWN

# setup and initialize relay (at start turned off)
relay = DigitalInOut(board.GP6)
relay.direction = Direction.OUTPUT
relay.value = False

def increase_temp(duration, max=150):
    start = time.monotonic()
    #temp_set should be control.temp_set!!!!!!!!!!!!!!!!!!!4
    global temp_set
    if temp_set < max:
        temp_set += 1
        update_lcd()
        while btn_up.value and temp_set < max:
            now = time.monotonic()
            if now-start > duration:
                for i in range(10):
                    temp_set += 1
                    time.sleep(0.02)
                    if not btn_up.value or temp_set == max:
                        break
                update_lcd()
    control.set_control_parameters(temp_set)
    if log_enabled:
        with open("/temp.txt", "w") as t:
            t.write(str(temp_set))

def decrease_temp(duration, min=20):
    start = time.monotonic()
    global temp_set
    if temp_set > min:
        temp_set -= 1
        update_lcd()
        while btn_down.value and temp_set > min:
            now = time.monotonic()
            if now-start > duration:
                for i in range(10):
                    temp_set -= 1
                    time.sleep(0.02)
                    if not btn_down.value or temp_set == min:
                        break
                update_lcd()
    control.set_control_parameters(temp_set)
    if log_enabled:
        with open("/temp.txt", "w") as t:
            t.write(str(temp_set))

def update_lcd():
    lcd.clear()
    lcd.message = "Temp: {0:0.1f} C\nSet: {1:0.0f} C".format(t.temperature, control.temp_set)

# log sensor data into csv file (if log_enabled)
def log_data(duration, temp, t_set, relay_log_value):
    with open("/log.txt", "a") as log:
        log.write("{0},{1},{2},{3}\n".format(str(duration), str(temp), str(t_set), str(relay_log_value)))
        log.flush()

def main():
    global temp_set
    start = time.monotonic()
    previous_temp = 0
    last_log = 0
    temp_delta = None
    temp_extremum_avg = None
    while True:
        now = time.monotonic()
        duration = now - start
        temp_actual = t.avg_temp_short(sensor.temperature)
        if math.fabs(temp_actual - previous_temp) > 0.1:
            update_lcd()
            print("current temperature: ", temp_actual)
            previous_temp = temp_actual
        if btn_down.value:
            decrease_temp(1)
        if btn_up.value:
            increase_temp(1)
# log has to be completely in a separat function / class
        if duration - last_log >= 1 and log_enabled:
            if relay.value:
                relay_log_value = temp_set + 0.5
            else:
                relay_log_value = temp_set - 0.5
            log_data(round(duration, 0), round(temp_actual, 1), temp_set, relay_log_value)
            last_log += 1

        direction = t.check_direction()
        inflexion_point = t.get_inflexion_point()
        t.get_min_max_temp(inflexion_point)
        if inflexion_point:
            control.inflexion_point_hit = True
            temp_delta = t.calculate_temp_delta()
            temp_extremum_avg = t.calculate_temp_extremum_avg()
        temp_state = t.define_state()
        control.calc_temp_diff(temp_actual)
        control.select_control_type(temp_actual, temp_state, direction, temp_extremum_avg, temp_delta)
        relay.value = control.heating_on
        if control.calibrate_stable_parameters():
            t.temp_max_list = []
            t.temp_min_list = []

main()