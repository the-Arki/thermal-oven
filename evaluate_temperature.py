import math

class Temperature():

    avg_temperature_list = []
    temperature_list = []
    temperature_list_counter = 1
    direction = "going_upwards"
    direction_counter = 1
    previous_direction = "going_upwards"
    temp_max_list = []
    temp_min_list = []
    temp_extremum_avg = 0.0
    temp_delta = 0.0
    state = "unstable"

    def __init__(self, temp):
        self.previous_temperature = temp
        self.temperature = temp

    def avg_temp_short(self, temp, measurements=10):
        "Return the average of the last 10 temp values"
        self.avg_temperature_list.append(temp)
        if len(self.avg_temperature_list) > measurements:
            self.avg_temperature_list.pop(0)
        self.temperature = sum(self.avg_temperature_list) / len(self.avg_temperature_list)
        return (self.temperature)

    def check_direction(self, checking_period=10):
        if self.direction_counter < checking_period:
            self.direction_counter += 1
        else:
#             print("previous temperature: ", self.previous_temperature)
#             print("current temperature: ", self.temperature)
            if self.temperature >= self.previous_temperature + 0.2:
                self.previous_temperature = self.temperature
                self.direction = "going_upwards"
            elif self.temperature <= self.previous_temperature - 0.2:
                self.direction = "going_downwards"
                self.previous_temperature = self.temperature
            self.direction_counter = 1
        return(self.direction)

    def get_inflexion_point(self):
        if self.previous_direction == self.direction:
            return None
        elif self.previous_direction == "going_downwards":
            self.previous_direction = self.direction
            return "min"
        else:
            self.previous_direction = self.direction
            return "max"

    def get_min_max_temp(self, extrema):
        if not extrema:
            if self.temperature_list_counter == 20:
                self.temperature_list.append(self.temperature)
                self.temperature_list_counter = 1
            else:
                self.temperature_list_counter += 1
        elif extrema == "min":
            self.temp_min_list.append(min(self.temperature_list))
            self.temperature_list = []
            print("temp min list: ", self.temp_min_list)
        elif extrema == "max":
            self.temp_max_list.append(max(self.temperature_list))
            self.temperature_list = []
            print("temp max list: ", self.temp_max_list)

    def calculate_temp_extremum_avg(self):
        max = self.temp_max_list
        min = self.temp_min_list
        if len(max) >= 2 and len(min) >= 2:
            avg = sum([max[-2], max[-1], min[-2], min[-1]]) / 4
            self.temp_extremum_avg = avg
            print("average: ", avg)
            return(avg)
        return None

    def calculate_temp_delta(self):
        if self.temp_max_list and self.temp_min_list:
            self.temp_delta = self.temp_max_list[-1] - self.temp_min_list[-1]
            print("temp_delta: ", self.temp_delta)
            return(self.temp_delta)
        return None

    def define_state(self):
        "define whether the process is stable or not"
        tmin_list = self.temp_min_list
        tmax_list = self.temp_max_list
        if len(tmin_list) < 2 or len(tmax_list) < 2:
            return("unstable")
        elif math.fabs(tmin_list[-1] - tmin_list[-2]) > 0.2 or \
            math.fabs(tmax_list[-1] - tmax_list[-2]) > 0.2:
            return("unstable")
        elif self.temperature > tmax_list[-1] + 0.2 or \
            self.temperature < tmin_list[-1] - 0.2:
            return("unstable")
        else:
            return("stable")