# -*- coding: utf-8 -*-
__author__ = 'nietaki'

from CarState import CarState

# initializing with default values
e = 0.2  # engine power
d = 0.02  # drag coefficient
p = 0.00125  # straightening coefficient
zeta = 0.1  # dampening coefficient

# now for the centrifugal force
# M_c = A * V^2 / r - B, where B is non-negative
A = 2.67330284184616
B = 0.855051077339845

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


def drag_coefficient():
    return d


def calculate_engine_power(v1, v2, throttle):
    """
    :param v1: float: velocity before one tick of throttle setting
    :param v2: float: velocity after one tick of throttle setting
    depends on proper drag coefficient. Works better on non-top speeds and non-zero throttle values
    """
    c = v2 - v1
    # c = a - v1 * d
    # e * throttle = c + v1 * d
    global e, d
    e = (c + v1 * d) / throttle
    return e


def velocity_after_time(v0, n, throttle):
    """
    http://www.wolframalpha.com/input/?i=v%28n%29+%3D+v%28n-1%29+*%281+-d%29+%2B+t
    :param n: time in ticks
    :param throttle: constant throttle position
    :param v0: starting speed
    """
    t = e * throttle
    v0 *= 1.0
    return (pow(1.0 - d, n) * (-v0*d - d*t + t) + (d-1) * t)/((d-1.0) * d)


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
    return max(0, v*v/r * A - B)

def a(throttle):
    return e * throttle

def b(v):
    return -v * d

def M_p(v, alpha):  # siła prostująca
    return -v * alpha * p


def M_d(omega, zeta):  # dampening force
    return -omega * zeta


def M(car):
    """
    :type car: CarState
    """
    ret = M_p(car.velocity, car.slip_angle)
    ret += M_d(car.angle_velocity, zeta)
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

    if car.in_piece_distance + tick_distance >= car.current_track_piece().true_piece_length(car.lane):
        car.in_piece_distance = (car.in_piece_distance + tick_distance) - car.current_track_piece().true_radius(car.lane)
        car.piece_position
    else:
        car.in_piece_distance += tick_distance




