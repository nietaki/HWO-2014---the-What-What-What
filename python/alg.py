__author__ = 'nietaki'

import datetime



def millis(t1, t2):
    td = t2 - t1
    return round(td.seconds * 1000 + td.microseconds / 1000)

# this bisect tries to find the LARGEST float value for which the function returns true
def my_bisect(lo, hi, iteration_count, f, max_time_millis=None):
    # we assert f(lo) is true and f(hi) is probably false
    # make sure you don't pass a value that's too low for you to go on!

    start_time = datetime.datetime.now()

    if f(hi):
        return hi


    for i in range(0, iteration_count):
        lo *= 1.0
        hi *= 1.0
        mid = (lo + hi) / 2
        guessed_success = f(mid)
        if guessed_success:
            lo = mid
        else:
            hi = mid
        if max_time_millis and millis(start_time, datetime.datetime.now()) > max_time_millis:
            return lo
    return lo

