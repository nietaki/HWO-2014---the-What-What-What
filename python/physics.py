__author__ = 'nietaki'

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


def estimate_centrifugal_force(v, r):
    #TODO add additional, more precise and complex ways
    return max(0, v*v/r * A - B)

