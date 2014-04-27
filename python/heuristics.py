# -*- coding: utf-8 -*-
__author__ = 'nietaki'

from BaseBot import BaseBot
from alg import *
import physics

# parę prostych botow i zastanowie się nad wygodna architekturą dla bota


class PhysicsTester(BaseBot):
    def __init__(self, sock, name, key):
        super(PhysicsTester, self).__init__(sock, name, key)
        #self.radius_speed_dict = {40: 4.8, 60: 5.5, 90: 6.6, 110: 7.3}
        self.radius_speed_dict = {40: 4.7, 60: 5.4, 90: 6.5, 110: 7.2}
        #self.radius_speed_dict = {40: 4.5, 60: 5.1, 90: 6.3, 110: 7.0}

    def on_car_positions(self, data, tick):
        piece_index = self.my_car().track_piece_index
        lane = self.my_car().lane()
        radius = self.track.true_radius(piece_index, lane)
        """
        game plan: sprawdzamy, czy trzeba zwalniać przed następnym zakrętem:
            jak tak, to zwalniamy
            jak nie, to sprawdzamy, czy jesteśmy w zakręcie:
             jak tak, to utrzymujemy prędkość adekwatną do zakrętu
             jak nie, to pełen gaz
        """
        if (self.my_car().slip_angle > 50 and self.my_car().angle_velocity > 1.0) or \
           (self.my_car().slip_angle < -50 and self.my_car().angle_velocity < -1.0):
            #print("That's too dangerous, brother!")
            self.throttle(0.3)
            return
        next_turn_id = self.track.next_bend_id(piece_index, min(radius, 150))
        distance_until_sharp_turn = self.track.distance_until_index(piece_index, self.my_car().in_piece_distance, next_turn_id, lane)
        if not distance_until_sharp_turn is None:
            target_velocity = self.radius_speed_dict[self.track.true_radius(next_turn_id, lane)]
            minimal_distance_to_break = physics.distance_to_break(self.my_car().velocity, target_velocity)
            if minimal_distance_to_break >= distance_until_sharp_turn and (self.my_car().velocity - target_velocity) > 0.1:
                self.throttle(0.0)
                #print("gotta slow down to {0}!".format(target_velocity))
                return
            else:
                0 == 0
                #print('there is a turn, but nothing serious yet, breaking distance is {0}, {1} available'.format(minimal_distance_to_break, distance_until_sharp_turn))

        if radius < 150:
            target_speed = self.radius_speed_dict[radius]
            #print("gonna set throttle to {0}".format(target_speed / 10))
            self.throttle(target_speed / 10)  # TODO rely on physics
        else:
            #print("full ahead, cap'n")
            self.throttle(1.0)


class PhysicsBisector(BaseBot):
    def __init__(self, sock, name, key):
        super(PhysicsBisector, self).__init__(sock, name, key)
        self.piece_look_ahead = 6

    def on_car_positions(self, data, tick):
        car = self.my_car()

        if not car.crashed:
            the_until = (car.track_piece_index + self.piece_look_ahead) % car.track.track_piece_count
            deduced_throttle = my_bisect(0.0, 1.0, 7, lambda t: physics.is_safe_until_simple(car, t, the_until, 0.0))
            print("decided to go on throttle {0} from {1} to {2}".format(deduced_throttle, car.track_piece_index, the_until))
            self.throttle(deduced_throttle, tick)
        else:
            self.ping()







