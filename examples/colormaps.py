#!/usr/bin/python3

"""colormaps.py: methods for temperature colormapping"""

from math import *

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "1.0.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "in development"

# Temperature range in Celsius (if supported by the thermal map mode)
minimimTemp = 15
maximumTemp = 80

# select linear in order to have a linear map from blue to red in the given range
def linear(temp10):
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)] 
    minval, maxval = 0, 4
    minTemp = minimimTemp * 10
    maxTemp = maximumTemp * 10
    if (temp10 < minTemp):
        return ''
    elif (temp10 > maxTemp):
        temp10 = maxTemp
    val = 3*((temp10 - minTemp)/maxTemp)+1
     
    max_index = len(colors)-1
    v = float(val-minval) / float(maxval-minval) * max_index
    i1, i2 = int(v), min(int(v)+1, max_index)
    (r1, g1, b1), (r2, g2, b2) = colors[i1], colors[i2]
    f = v - i1
     
    return '#%02x%02x%02x' % (int(r1 + f*(r2-r1)), int(g1 + f*(g2-g1)), int(b1 + f*(b2-b1)))

# shows in red anything whose temoerature is above 25C
def humanSpot(temp10):
    if (temp10 > 250):
        return "#FF0000"
    else:
        return ""