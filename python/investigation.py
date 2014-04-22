__author__ = 'nietaki'

from BaseBot import BaseBot


class KeimolaBreaker(BaseBot):
    def on_car_positions(self, data, tick):
        if self.my_car().velocity < 0.0001:
            self.throttle(0.5)
        elif self.my_car().track_piece_index == 36:
            self.throttle(1.0)
        elif self.my_car().track_piece_index == 38:
            self.throttle(0.0)
        else:
            self.ping()


class KeimolaAccelerator(BaseBot):
    def on_car_positions(self, data, tick):
        if self.my_car().velocity < 0.1:
            self.throttle(0.1)
        elif self.my_car().track_piece_index == 36:
            self.throttle(1.0)
        else:
            self.ping()


class GradualAccelerator(BaseBot):
    cur_throttle = 0.59
    target_ticks = 2000
    diff = 0.06/target_ticks

    def on_car_positions(self, data, tick):
        self.cur_throttle += self.diff
        if self.cur_throttle > 1.0:
            self.cur_throttle = 1.0
        self.throttle(self.cur_throttle)


class ConstThrottle(BaseBot):
    const_throttle = 0.5

    def on_car_positions(self, data, tick):
        self.throttle(self.const_throttle)


class ConstVelocity(BaseBot):
    """for now this only works on Keimola - the physics are hardcoded"""
    target_velocity = 5.0
    velocity_increase = 0.0

    def on_car_positions(self, data, tick):
        if self.my_car().velocity < self.target_velocity:
            self.throttle(1.0)
        elif self.my_car().velocity - self.target_velocity > 0.2:
            self.throttle(0.0)
        else:
            self.throttle(1.0 * self.target_velocity / 10)

    def on_lap_finished(self, data, tick):
        self.target_velocity += self.velocity_increase


class SwitchAndConstVelocity(BaseBot):
    """for now this only works on Keimola - the physics and switching are hardcoded"""
    def __init__(self, sock, name, key):
        #it sucks so bad we cannot really declare member variables outside of the constructor
        super(SwitchAndConstVelocity, self).__init__(sock, name, key)
        self.target_velocity = 5.0
        self.velocity_increase = 0.0
        self.already_switched = False

    def on_car_positions(self, data, tick):
        if not self.already_switched and tick > 0:
            self.already_switched = True
            self.switch_lane('Right')
        elif self.my_car().velocity < self.target_velocity:
            self.throttle(1.0)
        elif self.my_car().velocity - self.target_velocity > 0.2:
            self.throttle(0.0)
        else:
            self.throttle(1.0 * self.target_velocity / 10)

    def on_lap_finished(self, data, tick):
        self.target_velocity += self.velocity_increase


class ThresholdSpeedSearcher(BaseBot):
    def __init__(self, sock, name, key):
        super(ThresholdSpeedSearcher, self).__init__(sock, name, key)
        self.cruising_speed = 3.5
        self.targeted_radius = 90
        self.last_velocity = 0.0
        self.already_switched = True

    def on_car_positions(self, data, tick):
        me = self.my_car()
        if not self.already_switched and tick > 0:
            self.already_switched = True
            print("switching")
            self.switch_lane('Right')
        elif self.track.true_radius(me.track_piece_index, me.lane()) == self.targeted_radius:
            if abs(me.slip_angle) > 0.00001:
                print("{0} is over for radius {1}!".format(me.velocity, self.targeted_radius))
            else:
                print("{0} is under for radius {1}!".format(me.velocity, self.targeted_radius))
                self.throttle(1.0)
        else:
            self.cruising_speed = max(self.cruising_speed, me.velocity)
            self.throttle(self.cruising_speed / 10)

