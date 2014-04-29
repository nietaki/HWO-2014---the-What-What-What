# -*- coding: utf-8 -*-
import copy

__author__ = 'nietaki'

from BaseBot import BaseBot
from alg import *
import physics
import random

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
        self.piece_look_ahead = 5

    def on_car_positions(self, data, tick):
        car = self.my_car()

        if not car.crashed:
            the_until = (car.track_piece_index + self.piece_look_ahead) % car.track.track_piece_count
            deduced_throttle = my_bisect(0.0, 1.0, 6, lambda t: physics.is_safe_until_simple(car, t, the_until, 0.0))
            print("decided to go on throttle {0} from {1} to {2}".format(deduced_throttle, car.track_piece_index, the_until))
            self.throttle(deduced_throttle, tick)
        else:
            self.ping()

class AdvancedBisector(BaseBot):
    def __init__(self, sock, name, key):
        super(AdvancedBisector, self).__init__(sock, name, key)

    def on_car_positions(self, data, tick):
        car = self.my_car()

        if not car.crashed:
            cur_index = self.my_car().track_piece_index
            macro_index = self.track.macro_piece_map[cur_index]
            next_macro_beginning = self.track.reverse_macro_map[(macro_index + 1) % len(self.track.reverse_macro_map)]
            lane = car.lane()
            next_macro_beginning_piece = car.track.track_pieces[next_macro_beginning]
            next_macro_radius = next_macro_beginning_piece.true_radius(lane)
            #next_macro_target_speed = physics.estimate_stable_speed_at_angle(next_macro_radius, physics.crash_angle_buffered())
            next_macro_target_speed = physics.estimate_safe_speed_at_angle(next_macro_radius, physics.crash_angle_buffered())

            if car.current_track_piece().is_straight:
                if physics.distance_to_break(car.velocity, next_macro_target_speed) >= \
                car.track.distance_until_index(car.track_piece_index,
                                               car.in_piece_distance,
                                               next_macro_beginning,
                                               lane):
                    self.throttle(physics.throttle_to_reach_velocity(car.velocity, next_macro_target_speed), tick)
                else:
                    self.throttle(1.0, tick)
            else:
                # it's a bend!
                #FIXME: do the safe ending in a more intelligent way than adding one to the next piece index
                #FIXME: this is just copied from the other bot, we want velocities, not throttles
                the_until = (next_macro_beginning + 1) % car.track.track_piece_count
                deduced_throttle = my_bisect(0.0, 1.0, 6, lambda t: physics.is_safe_until_simple(car, t, the_until, 0.0))
                self.throttle(deduced_throttle, tick)
        else:
            self.ping()



class Cruiser(BaseBot):
    def __init__(self, sock, name, key):
        super(Cruiser, self).__init__(sock, name, key)

    def on_car_positions(self, data, tick):
        car = self.my_car()
        cur_index = car.track_piece_index

        if not car.crashed:
            # turning on Turbo at the beginning of the longest straight:
            if cur_index == self.track.index_of_the_beginning_of_the_longest_straight_piece and self.turbo_available:
                self.turbo("It's my time to shine!", tick)
                return

            macro_index = self.track.macro_piece_map[cur_index]
            next_macro_beginning = self.track.reverse_macro_map[(macro_index + 1) % len(self.track.reverse_macro_map)]
            lane = car.lane()
            distance_until_next_macro = car.track.distance_until_index(car.track_piece_index,
                                                                       car.in_piece_distance,
                                                                       next_macro_beginning,
                                                                       lane)

            next_macro_beginning_piece = car.track.track_pieces[next_macro_beginning]
            next_macro_radius = next_macro_beginning_piece.true_radius(lane)
            next_macro_target_speed = physics.estimate_stable_speed_at_angle(next_macro_radius, physics.crash_angle_buffered())

            ### SWITCH ###
            # should we consider switching? - is next piece a switch and is it legal now?
            if not car.is_switching() and not self.switch_initiated and self.track.next_piece(cur_index).switch and \
                            len(self.track.lanes) > 1 and car.velocity > physics.safe_speed:
                print(self.cars)
                print(map(lambda cr: cr.lane(), self.other_cars()))
                same_lane = filter(lambda cr: cr.lane() == lane, self.other_cars())
                print(same_lane)
                max_distance = 150.0
                print(max_distance)
                same_lane_and_close = filter(lambda cr: self.track.is_distance_less_than(cur_index, car.in_piece_distance, cr.track_piece_index, cr.in_piece_distance, lane, max_distance), same_lane)
                print(same_lane_and_close)
                if len(same_lane_and_close):
                    #there is somebody to go around

                    #TODO check if there is an opponent close'ish in front
                    dirs = car.possible_lane_switch_directions()
                    dir = random.choice(dirs)
                    car_other_lane = copy.copy(car)
                    car_other_lane.start_lane_index += dir
                    car_other_lane.end_lane_index += dir
                    if physics.check_with_annealing(car_other_lane):
                        print("going to switch lane to in the {0} direction".format(dir))
                        self.switch_lane_int(dir, tick)
                        return
                    else:
                        print("staying here, switching is not safe!")

            if self.switch_initiated:
                print('reducing speed to be safe')
                self.throttle(0.0, tick)
                return
            ### end SWITCH ###

            if car.current_track_piece().is_straight:
                # straight!
                should_run_like_hell = ((self.is_race() and \
                                         car.lap == self.lap_count() - 1) or \
                                        (not self.is_race() and car.last_crashed_lap != car.lap)) and \
                                         macro_index == len(self.track.reverse_macro_map) - 1 and \
                                         car.current_track_piece().is_straight
                if should_run_like_hell:
                    print("gotta go fast!")
                    if self.turbo_available:
                        self.turbo("it's my last chance at fame and fortune!", tick)
                    else:
                        self.throttle(1.0, tick)
                    return


                next_macro_target_speed = physics.estimate_safe_speed_at_angle(next_macro_radius, physics.crash_angle_buffered())

                # simulating the car braking to the safe speed
                car_at_next_macro = physics.simulate_straight_with_breaking_to_speed(car, distance_until_next_macro, next_macro_target_speed)

                # end of the simulation with annealing
                macro_plus_1 = (macro_index + 1) % len(self.track.reverse_macro_map)
                # getting the best speed for the bend
                deduced_speed = physics.estimate_optimal_speed_at_bend_with_annealing(car_at_next_macro,
                                                                                      car.track.reverse_macro_map[macro_plus_1],
                                                                                      True)

                # planning the breaking, now with better values
                # checking if we can afford it
                # velocity and travelled distance in one step of full throttle
                next_velocity, next_distance = physics.velocity_and_distance_step(car.velocity, 1.0)
                # distance needed to break
                breaking_distance = physics.distance_to_break(next_velocity, max(deduced_speed, next_macro_target_speed))
                if breaking_distance + next_distance < distance_until_next_macro:
                    self.throttle(1.0, tick)
                else:
                    self.throttle(0.0, tick)

            else:
                # it's a bend!
                the_until = (next_macro_beginning + 1) % car.track.track_piece_count
                deduced_speed = physics.estimate_optimal_speed_at_bend_with_annealing(car, the_until)
                self.throttle(physics.throttle_to_reach_velocity(car.velocity, deduced_speed), tick)
        else:
            self.ping(tick)



