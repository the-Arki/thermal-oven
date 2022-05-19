import math
import time
from evaluate_temperature import Temperature
from control import ControlTemperature
from setup import *

# set initial required temperature
with open("/temp.txt", "r") as t:
    temp_set = int(t.read())
print("initial temp_set: ", temp_set)

# initialize Temperature class
t = Temperature(temp_actual)
control = ControlTemperature(temp_set)

# Built-in LED lights for 1 sec at start
led.value = True
time.sleep(1)
led.value = False

# initialize log pin
if log_pin.value:
    log_enabled = True
else:
    log_enabled = False

## log the number of restarts
# def count_restarts():
#     restarts = {}
#     if log_enabled:
#         with open("/restarts.txt", "r") as rs:
#             restarts = eval(rs.read())
#         if not str(control.temp_set) in restarts:
#             restarts[str(control.temp_set)] = 1
#         else:
#             restarts[str(control.temp_set)] += 1
#         with open("/restarts.txt", "w") as rs:
#             rs.write(str(restarts))
#     print('restarts: ', restarts)

# count_restarts()        

# initialize lcd
lcd.clear()
lcd.message = "Temp: {0:0.1f} C\nSet: {1:0.0f}".format(temp_actual, control.temp_set)

# initialize relay (at start turned off)
relay.value = False

def increase_temp(duration, max=150):
    start = time.monotonic()
    stop = time.monotonic()
    now = time.monotonic()
    prev_value = 0
    while now - stop < 3:
        now = time.mononotic()
        if not btn_up.value:
            prev_value = 0
        if control.temp_set < max and not prev_value and btn_up.value:
            prev_value = 1
            control.temp_set += 1
            update_lcd()
        while btn_up.value and control.temp_set < max:
            now = time.monotonic()
            stop = time.monotonic()
            if now-start > duration:
                for i in range(10):
                    control.temp_set += 1
                    time.sleep(0.02)
                    if not btn_up.value or control.temp_set == max:
                        break
                update_lcd()
    control.set_control_parameters(control.temp_set)
    t.temp_max_list = []
    t.temp_min_list = []
    if log_enabled:
        with open("/temp.txt", "w") as t:
            t.write(str(control.temp_set))

def decrease_temp(duration, min=20):
    start = time.monotonic()
    stop = time.monotonic()
    now = time.monotonic()
    prev_value = 0
    while now - stop < 3:
        if not btn_down.value:
            prev_value = 0
        if control.temp_set > min and not prev_value and btn_down.value:
            prev_value = 1
            control.temp_set -= 1
            update_lcd()
        while btn_down.value and control.temp_set > min:
            now = time.monotonic()
            stop = time.monotonic()
            if now-start > duration:
                for i in range(10):
                    control.temp_set -= 1
                    time.sleep(0.02)
                    if not btn_down.value or control.temp_set == min:
                        break
                update_lcd()
    control.set_control_parameters(control.temp_set)
    t.temp_max_list = []
    t.temp_min_list = []
    if log_enabled:
        with open("/temp.txt", "w") as t:
            t.write(str(control.temp_set))

def update_lcd():
    lcd.clear()
    lcd.message = "Temp: {0:0.1f} C\nSet: {1:0.0f} C\nDelta: {2:0.2f} C\nAverage: {3: 0.2f} C".format(t.temperature, control.temp_set, t.temp_delta, t.temp_extremum_avg)

# log sensor data into csv file (if log_enabled)
def log_data(duration, temp, t_set, relay_log_value):
    with open("/log.txt", "a") as log:
        log.write("{0},{1},{2},{3}\n".format(str(duration), str(temp), str(t_set), str(relay_log_value)))
        log.flush()

def main():
    # start = time.monotonic()
    previous_temp = 0
    # last_log = 0
    temp_delta = None
    temp_extremum_avg = None
    while True:
        # now = time.monotonic()
        # duration = now - start
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
        # if duration - last_log >= 10 and log_enabled:
        #     if relay.value:
        #         relay_log_value = control.temp_set + 0.5
        #     else:
        #         relay_log_value = control.temp_set - 0.5
        #     log_data(round(duration, 0), round(temp_actual, 1), control.temp_set, relay_log_value)
        #     last_log += 10

        direction = t.check_direction()
        inflexion_point = t.get_inflexion_point()
        t.get_min_max_temp(inflexion_point)
        if inflexion_point:
            control.inflexion_point_hit = True
            control.inflexion_point = inflexion_point
            temp_delta = t.calculate_temp_delta()
            temp_extremum_avg = t.calculate_temp_extremum_avg()
        temp_state = t.define_state()
        control.calc_temp_diff(temp_actual)
        control.select_control_type(temp_actual, temp_state, direction, temp_extremum_avg, temp_delta)
        relay.value = control.heating_on
        # comment out below if not calibrating
        # if control.calibrate_stable_parameters():
        #     t.temp_max_list = []
        #     t.temp_min_list = []

if __name__ == "__main__":
    main()