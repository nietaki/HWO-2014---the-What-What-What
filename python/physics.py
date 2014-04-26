# -*- coding: utf-8 -*-
__author__ = 'nietaki'

from alg import my_bisect
import copy
import numpy as np
from collections import deque, namedtuple


class CarState(object):
    """stores all the state of a car (position, velocity and others), ours or theirs. Most of the info comes from the server
    messages, the throttle comes from the bot"""

    def __init__(self, track_object, game_init_car_fragment):
        """
        :type track_object: Track
        """
        self.name = game_init_car_fragment['id']['name']
        self.color = game_init_car_fragment['id']['color']
        self.dimensions = game_init_car_fragment['dimensions']
        self.track = track_object

        self.throttle = 0.0

        #basic stats
        self.tick = 0

        self.track_piece_index = 0
        self.in_piece_distance = 0.0
        self.start_lane_index = 0
        self.end_lane_index = 0

        self.velocity = 0.0

        """basically velocity delta"""
        self.acceleration = 0.0

        #from gameInit
        self.lanes = None
        self.car_dimensions = None
        self.race_session = None

        #from carPositions
        self.piece_position = None
        self.slip_angle = 0.0

        self.angle_velocity = 0.0
        self.angle_acceleration = 0.0

        self.crashed = False

        self.vaoMsq = deque()

    def crash(self):
        self.crashed = True

    def spawn(self):
        self.crashed = False

    def set_throttle(self, throttle):
        self.throttle = throttle

    def relative_angle(self):
        """ relative meaning it always goes >0 on bends """
        return self.track.bend_direction(self.track_piece_index) * self.slip_angle

    def lane(self):
        return self.end_lane_index

    def is_switching(self):
        return self.start_lane_index != self.end_lane_index

    def current_track_piece(self):
        return self.track.track_pieces[self.track_piece_index]

    VaoMs = namedtuple('VaoMs', 'velocity alpha omega M straight')

    def on_car_position(self, car_data, new_tick, my_car):
        #FIXME this is a mess
        new_slip_angle = car_data['angle']
        new_angle_velocity = new_slip_angle - self.slip_angle

        self.angle_acceleration = new_angle_velocity - self.angle_velocity
        self.angle_velocity = new_angle_velocity

        self.slip_angle = new_slip_angle
        self.piece_position = car_data['piecePosition']
        self.tick = new_tick

        self.start_lane_index = self.piece_position['lane']['startLaneIndex']
        self.end_lane_index = self.piece_position['lane']['endLaneIndex']

        new_track_piece_index = self.piece_position['pieceIndex']
        new_in_piece_distance = self.piece_position['inPieceDistance']

        #FIXME this won't work correctly when switching on bends - the track lengths vary
        new_velocity = self.track.distance_diff(self.track_piece_index, self.in_piece_distance,
                                                new_track_piece_index,
                                                new_in_piece_distance, self.lane())
        self.acceleration = (new_velocity - self.velocity)

        if not self.velocity and new_velocity and my_car:
            calculate_engine_power_from_first_tick(new_velocity, 1.0)  #TODO set to 1.0 just in case

        self.velocity = new_velocity

        self.track_piece_index = new_track_piece_index
        self.in_piece_distance = new_in_piece_distance

        # at the very end, the straightening forces:
        t = self.VaoMs(self.velocity, self.slip_angle, self.angle_velocity, self.angle_acceleration,
                       self.track.track_pieces[self.track_piece_index].is_straight)
        self.vaoMsq.append(t)
        while len(self.vaoMsq) > 3:
            self.vaoMsq.popleft()

        if len(self.vaoMsq) == 3:
            #                      straight                                      alpha != 0
            if all(map(lambda tup: tup.straight, self.vaoMsq)) and all(map(lambda tup: tup.alpha != 0, self.vaoMsq)):
                v0 = self.vaoMsq[0].velocity
                alpha0 = self.vaoMsq[0].alpha
                omega0 = self.vaoMsq[0].omega
                M0 = self.vaoMsq[1].M
                v1 = self.vaoMsq[1].velocity
                alpha1 = self.vaoMsq[1].alpha
                omega1 = self.vaoMsq[1].omega
                M1 = self.vaoMsq[2].M
                estimate_p_and_zeta(v0, alpha0, omega0, M0, v1, alpha1, omega1, M1)


                #print("tick: {0}, tick_delta: {1},distance_delta: {2}, velocity: {3}, acceleration: {4}".
                #      format(self.tick,
                #             self.tick_delta,
                #             self.distance_delta,
                #             self.velocity,
                #             self.acceleration))

# the actual physics

# initializing with default values
e = 0.2  # engine power
d_calculation_velocity = 0.1
d = 0.02  # drag coefficient
p_and_zeta_estimated = False
p = 0.00125  # straightening coefficient
zeta = 0.1  # dampening coefficient

# now for the centrifugal force
# M_c = A * V^2 / r - B, where B is non-negative
A = 2.67330284184616
B = 0.855051077339845

crash_angle = 50


def calculate_drag_coefficient(v1, v2):
    """
    :param v1: float: velocity before one tick of throttle set to 0
    :param v2: float: velocity after one tick of throttle set to 0

    calculates the d (drag coeff) based on two velocities and
    v2 = v1 - v1 * d
    v2 = v1(1 - d)
    d = 1 - v2/v1

    works better with higher speeds
    """
    v2 *= 1.0
    global d
    d = 1.0 - (v2 / v1)
    return d


def is_safe_state(car_state):
    """
    :type car_state: CarState
    """
    tick_count = 4
    safe = abs(car_state.slip_angle) < crash_angle
    #safe_future = abs(car_state.slip_angle + car_state.angle_velocity * tick_count) < crash_angle
    safe_future = True
    return safe and safe_future


def is_safe_until_simple(input_car_state, throttle, target_piece_id, target_in_piece_distance):
    b, cs = is_safe_until(input_car_state, throttle, target_piece_id, target_in_piece_distance)
    return b


def is_safe_until(input_car_state, throttle, target_piece_id, target_in_piece_distance):
    """
    :param car_state: input car_state. It won't be modified
    :type car_state: CarState
    :param throttle: throttle to be applied until the place
    :param target_piece_id:
    :param target_in_piece_distance:
    :return: modified CarState at the end of the action
    """
    print("checking if {0} is safe until {1}, distance {2}".format(throttle, target_piece_id, target_in_piece_distance))
    car_state = copy.copy(input_car_state)
    counter = 0;
    while car_state.track_piece_index != target_piece_id or car_state.in_piece_distance < target_in_piece_distance:
        if not is_safe_state(car_state):
            print("it is not")
            return False, car_state
        step(car_state, throttle)
        counter += 1

    print("it IS!, based on {0} ticks".format(counter))
    return True, car_state


def calculate_engine_power_from_first_tick(v0, throttle):
    global e;
    e = v0 / throttle
    print("e estimated to be {0}".format(e))


def calculate_drag(v1, v2, throttle):
    """
    depends on knowing the engine power
    :param v1: velocity before the throttle tick
    :param v2: velocity after the throttle tick
    :param throttle: the throttle set
    """
    global d, d_calculation_velocity
    if v1 > d_calculation_velocity:
        c = v2 - v1
        a = e * throttle
        b = a - c  # b is positive
        d = b / v1
        d_calculation_velocity = v1


#def calculate_engine_power(v1, v2, throttle):
#    """
#    :param v1: float: velocity before one tick of throttle setting
#    :param v2: float: velocity after one tick of throttle setting
#    depends on proper drag coefficient. Works better on non-top speeds and non-zero throttle values
#    """
#    c = v2 - v1
#    # c = a - v1 * d
#    # e * throttle = c + v1 * d
#    global e, d
#    e = (c + v1 * d) / throttle
#    return e


def velocity_after_time(v0, n, throttle):
    """
    http://www.wolframalpha.com/input/?i=v%28n%29+%3D+v%28n-1%29+*%281+-d%29+%2B+t
    :param n: time in ticks
    :param throttle: constant throttle position
    :param v0: starting speed
    """
    t = e * throttle
    v0 *= 1.0
    return (pow(1.0 - d, n) * (-v0 * d - d * t + t) + (d - 1) * t) / ((d - 1.0) * d)


def velocity_and_distance_step(v0, throttle):
    """
    :returns (new_speed, distance_travelled) after one tick
    """
    v1 = v0 + (throttle * e - v0 * d)
    return v1, v0


def distance_to_break(v0, target_velocity):
    """
    :returns the distance needed to break to target velocity
    this function works in linear time instead of constant, because I don't have time for mathematics now
    """
    dist = 0.0
    v = v0
    while v > target_velocity:
        v, new_dist = velocity_and_distance_step(v, 0.0)
        dist += new_dist
    return dist


def velocity_after_distance(v0, distance, throttle):
    """
    see distance_to_break
    """
    dist = 0.0
    v = v0
    while dist < distance:
        v, new_dist = velocity_and_distance_step(v, throttle)
        dist += new_dist
    return v


def estimate_M_c(v, r):
    #TODO add additional, more precise and complex ways
    ret = max(0, v * v / r * A - B)
    #print("estimated M_c={0} for v={1} and r={2}".format(ret, v, r))
    return ret


def estimate_p_and_zeta(v0, alpha0, omega0, M0, v1, alpha1, omega1, M1):
    """
    only to be used in straight line after exiting a curve
    """
    #x0=p x1=zeta
    #
    global p, zeta, p_and_zeta_estimated

    if p_and_zeta_estimated:
        return
    b = np.array([M0, M1])
    a = np.array([[-v0 * alpha0, -omega0], [-v1 * alpha1, -omega1]])
    pz = np.linalg.solve(a, b)

    p = pz[0]
    zeta = pz[1]
    print("estimated p={0}, zeta={1}".format(p, zeta))
    p_and_zeta_estimated = True

def a(throttle):
    return e * throttle


def b(v):
    return -v * d


def M_p(v, alpha):  # siła prostująca
    return -v * alpha * p


def M_d(omega):  # dampening force
    return -omega * zeta


def M(car):
    """
    :type car: CarState
    """
    ret = M_p(car.velocity, car.slip_angle)
    ret += M_d(car.angle_velocity)
    ret += estimate_M_c(car.velocity, car.current_track_piece().true_radius(car.lane()))
    return ret


def step(car, throttle=None):
    """
    :type car:CarState
    """
    if throttle is None:
        throttle = car.throttle

    c = a(throttle) + b(car.velocity)

    #first we update angles with the old velocity and so on values
    #only afterwards we update the speed, velocity and acceleration, since they are not affected
    car.angle_acceleration = M(car)
    car.angle_velocity = car.angle_velocity + car.angle_acceleration
    car.slip_angle = car.slip_angle + car.angle_velocity

    car.acceleration = c
    car.velocity = car.velocity + car.acceleration

    tick_distance = car.velocity

    if car.in_piece_distance + tick_distance >= car.current_track_piece().true_length(car.lane()):
        car.in_piece_distance = (car.in_piece_distance + tick_distance) - car.current_track_piece().true_length(
            car.lane())
        car.track_piece_index = (car.track_piece_index + 1) % car.track.track_piece_count
    else:
        car.in_piece_distance += tick_distance




