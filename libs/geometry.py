#!/usr/bin/python3

"""geometry.py: collection of geometrical functons """

from math import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in development"
__requiredfirmware__ = ""


def isPointInPoly(point, polygon):
    crossings = 0
    for i in range(1,len(polygon)):
        if find_intersection([[0,0],point],[polygon[i-1],polygon[i]]):
            crossings += 1
    if find_intersection([[0, 0], point], [polygon[0], polygon[-1]]):
        crossings += 1
    return (crossings % 2) != 0


def find_intersection( lineA, lineB):

    p0 = list(map(float, lineA[0]))
    p1 = list(map(float, lineA[1]))
    p2 = list(map(float, lineB[0]))
    p3 = list(map(float, lineB[1]))

    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]

    denom = s10_x * s32_y - s32_x * s10_y
    if denom == 0 : return None # collinear

    denom_is_positive = denom > 0
    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]
    s_numer = s10_x * s02_y - s10_y * s02_x
    if (s_numer < 0) == denom_is_positive : return None # no collision

    t_numer = s32_x * s02_y - s32_y * s02_x
    if (t_numer < 0) == denom_is_positive : return None # no collision

    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive : return None # no collision
    # collision detected
    t = t_numer / denom
    intersection_point = [ p0[0] + (t * s10_x), p0[1] + (t * s10_y)]

    return intersection_point


def distancePoint(pointA, pointB):
    return hypot(pointB[0] - pointA[0], pointB[1] - pointA[1])


def distanceFromCircle(centre, radius, point):
    return abs(hypot(point[0] - centre[0], point[1] - centre[1]) - radius)


def distanceFromDiamond(centre, radius, point):
    cornerA = [centre[0]-radius,centre[1]]
    cornerC = [centre[0]+radius,centre[1]]
    cornerD = [centre[0],centre[1]-radius]
    cornerB = [centre[0],centre[1]+radius]
    return distanceFromPoly([cornerA,cornerB,cornerC,cornerD, cornerA],point)


def distanceFromLine(line, point):

    x1 = line[0][0]
    y1 = line[0][1]
    x2 = line[1][0]
    y2 = line[1][1]
    x3 = point[0]
    y3 = point[1]

    px = x2-x1
    py = y2-y1

    crossP = px*px + py*py

    u = ((x3 - x1) * px + (y3 - y1) * py) / float(crossP)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    dist = hypot(dx, dy)

    return dist


def distanceFromPoly(poly,point):

    minDistance = 99999999999

    for i in range(1,len(poly)):
        newDistance = distanceFromLine([poly[i-1],poly[i]],point)
        if newDistance < minDistance: minDistance = newDistance

    return minDistance


def distanceFromRect(rect,point):

    rect2poly = [rect[0], [rect[1][0],rect[0][1]], rect[1], [rect[0][0],rect[1][1]], rect[0]]
    return distanceFromPoly(rect2poly, point)


