__author__ = 'nietaki'

# this bisect tries to find the LARGEST float value for which the function returns true

def my_bisect(lo, hi, iteration_count, f):
    # we assert f(lo) is true and f(hi) is probably false
    # make sure you don't pass a value that's too low for you to go on!
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
    return lo

