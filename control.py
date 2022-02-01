import time
import math

class ControlTemperature():

    heat_up_phase = False
    heating_on = False
    heat_up_start = time.monotonic()
    heating_duration = int
    temperature_difference = ""
    inflexion_point_hit = False
    calibration_counter = 0
    with open("control_parameters.txt", "r") as d:
        control_parameters_dict = eval(d.read())

    def __init__(self, temp_set):
        self.temp_set = temp_set

    def set_control_parameters(self, temp_set):
        self.temp_set = temp_set
        if temp_set not in self.control_parameters_dict:
            dictionary = self.control_parameters_dict
            lower = temp_set - temp_set%10
            higher = lower + 10
            if (lower or higher) not in dictionary:
                print("out of range")
            else:
                dictionary[temp_set] = {}
                for key in dictionary[lower]:
                    dictionary[temp_set][key] = ((10-temp_set%10*dictionary[lower][key]) + 
                                                 temp_set%10*dictionary[higher][key])/10
                print("control parameters: ", dictionary[temp_set])

    def calc_temp_diff(self, temp_actual):
        temp_diff = self.temp_set - temp_actual
        if temp_diff > 30:
            self.temperature_difference = "30+"
        elif 15 < temp_diff <= 30:
            self.temperature_difference = "15+"
        elif 5 < temp_diff <= 15:
            self.temperature_difference = "5+"
        elif temp_diff <= 5:
            self.temperature_difference = "5-"

    def select_control_type(self, temp_actual, temp_state, direction, temp_extremum_avg, temp_delta):
        now = time.monotonic()
        if self.heat_up_phase:
            if self.heating_on:
                if now - self.heat_up_start > self.heating_duration:
                    self.heating_on = False
            elif now - self.heat_up_start > 100:
                self.heat_up_phase = False
        elif temp_state == "unstable":
            self.control_temperature(direction, temp_actual)
            self.calibration_counter = 0
        else:
            if self.inflexion_point_hit:
                print("state: stable")
                self.adjust_stable_parameters(temp_extremum_avg, temp_delta, temp_state)
            self.control_temperature(direction, temp_actual)


    def control_temperature(self, direction, temp_actual):
        lower_limit = self.control_parameters_dict[self.temp_set]["lower_limit"]
        upper_limit = self.control_parameters_dict[self.temp_set]["upper_limit"]
        if direction == "going_upwards":
            if self.temp_set + lower_limit > temp_actual:
                self.heat_up_start = time.monotonic()
                self.heat_up_phase = True
                self.heating_on = True
                self.heating_duration = self.control_parameters_dict \
                    [self.temp_set][self.temperature_difference]
                print(self.control_parameters_dict[self.temp_set])
        elif direction == "going_downwards":
            if self.temp_set + upper_limit > temp_actual:
                self.heat_up_start = time.monotonic()
                self.heat_up_phase = True
                self.heating_on = True
                self.heating_duration = self.control_parameters_dict \
                    [self.temp_set][self.temperature_difference]
                print(self.control_parameters_dict[self.temp_set])

    def adjust_stable_parameters(self, temp_extremum_avg, temp_delta, temp_state):
        self.inflexion_point_hit = False
        if temp_state != "stable":
            return
        if math.fabs(temp_extremum_avg - self.temp_set) > 0.1:
            difference = self.temp_set - temp_extremum_avg
            self.control_parameters_dict[self.temp_set]["lower_limit"] += difference
            self.control_parameters_dict[self.temp_set]["upper_limit"] += difference
            self.calibration_counter = 0
        elif temp_delta > 1:
            self.control_parameters_dict \
                [self.temp_set][self.temperature_difference] -= 0.1
            self.calibration_counter = 0
        else:
            self.calibration_counter += 1
        print("new control parameters: ", self.control_parameters_dict[self.temp_set])
        print("calibration_counter: ", self.calibration_counter)

    def calibrate_stable_parameters(self):
        if self.calibration_counter >= 4 and self.temp_set <= 140:
            self.calibration_counter = 0
            with open("control_parameters.txt", "w") as d:
                d.write(str(self.control_parameters_dict))
            print("control parameters: ", self.control_parameters_dict[self.temp_set])
            self.temp_set += 10
            print("new temp_set: ", self.temp_set)
            with open("/temp.txt", "w") as t:
                t.write(str(self.temp_set))
            return True
        else:
            return False
