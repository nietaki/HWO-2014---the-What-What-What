__author__ = 'nietaki'

from BaseBot import BaseBot


class KeimolaBreaker(BaseBot):
    def on_car_positions(self, data):
        if self.my_car().velocity < 0.0001:
            self.throttle(0.5)
        elif self.my_car().track_piece_index == 36:
            self.throttle(1.0)
        elif self.my_car().track_piece_index == 38:
            self.throttle(0.0)
        else:
            self.ping()


class KeimolaAccelerator(BaseBot):
    def on_car_positions(self, data):
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

    def on_car_positions(self, data):
        self.cur_throttle += self.diff
        if self.cur_throttle > 1.0:
            self.cur_throttle = 1.0
        self.throttle(self.cur_throttle)


class ConstThrottle(BaseBot):
    const_throttle = 0.5

    def on_car_positions(self, data):
        self.throttle(self.const_throttle)


class ConstVelocity(BaseBot):
    """for now this only works on Keimola - the physics are hardcoded"""
    target_velocity = 5.0

    def on_car_positions(self, data):
        if self.my_car().velocity < self.target_velocity:
            self.throttle(1.0)
        else:
            self.throttle(1.0 * self.target_velocity / 10)
