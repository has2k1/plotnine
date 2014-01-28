from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import math

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def convert_if_int(x):
    if int(x)==x:
        return int(x)
    else:
        return x


def calc_axis_breaks(minval, maxval, nlabs=None):
    #if 1==1:
    if nlabs is None:
        diff = maxval - minval
        base10 = math.log10(diff)
        power = math.floor(base10)
        base_unit = 10**power
        step = base_unit / 2
        if minval % step!=0:
            minval = abs(minval) % step + minval

        labs = list(drange(minval, maxval, step))

        return labs
    else:
        diff = maxval - minval
        tick_range = diff / float(nlabs)
        power = math.ceil(math.log(tick_range, 10))
        base_unit = round(tick_range / (10**power), 1) * 10**power
        minval = base_unit * round(minval/base_unit)
        maxval = base_unit * round(1 + maxval/base_unit)
        
        labs = list(drange(minval, maxval, base_unit))
        labs = [convert_if_int(lab) for lab in labs]
        return labs
