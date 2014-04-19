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
    cur_throttle = 0.1
    target_ticks = 2000
    diff = 1.0/target_ticks

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

    def on_car_positions(self, data, tick):
        if self.my_car().velocity < self.target_velocity:
            self.throttle(1.0)
        else:
            self.throttle(1.0 * self.target_velocity / 10)




class SwitchAndConstVelocity(BaseBot):
    """for now this only works on Keimola - the physics and switching are hardcoded"""
    def __init__(self, sock, name, key):
        #it sucks so bad we cannot really declare member variables outside of the constructor
        super(SwitchAndConstVelocity, self).__init__(sock, name, key)
        self.target_velocity = 5.0
        self.already_switched = False


    def on_car_positions(self, data, tick):
        if not self.already_switched and tick > 0:
            self.already_switched = True
            self.switch_lane('Right')
        elif self.my_car().velocity < self.target_velocity:
            self.throttle(1.0)
        else:
            self.throttle(1.0 * self.target_velocity / 10)