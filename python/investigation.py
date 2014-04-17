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