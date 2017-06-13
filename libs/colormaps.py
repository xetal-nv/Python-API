#!/usr/bin/python3

"""colormaps.py: methods for temperature colormapping"""

from math import *

# from matplotlib import *
# import matplotlib.pyplot as plt

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"

# Temperature range in Celsius (if supported by the thermal map mode)
minimimTemp = 15
maximumTemp = 40

# provide scale in mm when relevant
SCALE = 100

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
    val = 3 * ((temp10 - minTemp) / maxTemp) + 1

    max_index = len(colors) - 1
    v = float(val - minval) / float(maxval - minval) * max_index
    i1, i2 = int(v), min(int(v) + 1, max_index)
    (r1, g1, b1), (r2, g2, b2) = colors[i1], colors[i2]
    f = v - i1

    return '#%02x%02x%02x' % (int(r1 + f * (r2 - r1)), int(g1 + f * (g2 - g1)), int(b1 + f * (b2 - b1)))


# shows in red anything whose temoerature is above 25C
def thresholdMap(temp10):
    if (temp10 > 250):
        return "#FF0000"
    else:
        return ""


# uses standard matplotlib colorscales to make the color mapping
# change the value of modifier to compress (<1) or inflate (<1) mid range
def matplotlibScale(temp10, modifier=1, colorScale="ocean"):
    minTemp = minimimTemp * 10
    maxTemp = maximumTemp * 10
    if (temp10 < minTemp):
        return ''
    elif (temp10 > maxTemp):
        temp10 = maxTemp
    val = (temp10 / maxTemp) ** modifier
    import matplotlib.pyplot as plt
    Scale = plt.get_cmap(colorScale)
    colors = (list(map(lambda x: trunc(x * 255), Scale(val))))
    return ('#%02x%02x%02x' % (colors[0], colors[1], colors[2]))


# same as above but it uses the actual minimum and maximum values insteaf of the given range
def matplotlibScaleAdapted(temp10, minTemp, maxTemp, modifier=1, colorScale="hot"):
    if (temp10 == 0):
        return ''
    val = ((temp10 - minTemp) / (maxTemp - minTemp)) ** modifier
    import matplotlib.pyplot as plt
    Scale = plt.get_cmap(colorScale)
    colors = (list(map(lambda x: trunc(x * 255), Scale(val))))
    return ('#%02x%02x%02x' % (colors[0], colors[1], colors[2]))


# uses three colors for the temperature text only with respect to a referebce value
def threeWayColor(temp10, avgTemp, variation=0):
    if (abs(temp10 - avgTemp) <= variation):
        return "black"
    elif (temp10 > (avgTemp + variation)):
        return "red"
    else:
        return "blue"

# the following methods are used to properly shade a given color
# as from KinseiClient the larger the value the more likely is the decetion
# and the bigther the color
def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return int(val)


def colorscale(hexstr, scalefactor):
    hexstr = hexstr.strip('#')

    if scalefactor < 0 or len(hexstr) != 6:
        return hexstr

    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)

    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)

    return "#%02x%02x%02x" % (r, g, b)