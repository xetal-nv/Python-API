#!/usr/bin/python3

"""thermalmap.py: basic graphical viewer for the thermal map"""

from math import *
from tkinter import *
import os

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')
import KinseiClient
import gui
import colormaps

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.2.5"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "july2017 or later"


# set the viewing window
maxScreenX = 1000  # maximum X size of screen window in pixels
maxScreenY = 800  # maximum Y size of screen window in pixels
offset = 10  # padding offset in pixels

# set the type of colormap (see colormaps.py for types of maps available)
whichcoloring = colormaps.matplotlibScale

# set if average temperature needs to be shown
showAverageTemp = True

# show colormapping or temperatures
showColorMapping = False

# Error on average for textColorMapping
minVariation = 0.1

if showAverageTemp:
    from statistics import mean


# this class shows how to visualise tracking with tkinter
class ThermalMap:
    def __init__(self):
        self.demoKit = None
        self.connected = False
        self.canvas = None
        self.roomSize = None
        self.master = None
        self.realVertex = None
        self.screenX = 0
        self.screenY = 0
        self.ip = None
        self.coloring = None
        self.averageTemp = 0
        self.thermalMapSettings = None
        self.grid = None

    def connect(self, ip, whichMap=whichcoloring):
        try:
            self.coloring = whichMap
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
            self.averageTemp = 0
            self.ip = ip
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    # the KinseiClient class provides coordinates in mm and absolute
    # here we scale to cm and made them relative to our canvas
    def adjustedCoordinates(self, coordinates):
        coordX = int((coordinates[0] / 10) * ((self.screenX * 10) / self.roomSize[0])) + offset
        coordY = int((coordinates[1] / 10) * ((self.screenY * 10) / self.roomSize[1])) + offset
        return [coordX, coordY]

    def defineCanvas(self):
        boundingBoxRatio = self.roomSize[0] / self.roomSize[1]
        screenRatio = maxScreenX / maxScreenY
        if screenRatio < 1:
            # portrait screen
            if (boundingBoxRatio < 1) and (screenRatio > boundingBoxRatio):
                # We need to scale from the height
                yMax = maxScreenY
                yMin = 0
                theOtherDimension = trunc((yMax - yMin) * boundingBoxRatio)
                xMin = trunc((maxScreenX - theOtherDimension) / 2)
                xMax = xMin + theOtherDimension
            else:
                # We need to scale from the width
                xMin = 0
                xMax = maxScreenX
                theOtherDimension = trunc((xMax - xMin) / boundingBoxRatio)
                yMin = 0
                yMax = yMin + theOtherDimension
        else:
            # landscape screen
            if (boundingBoxRatio > 1) and (screenRatio < boundingBoxRatio):
                # We need to scale from the width
                xMin = 0
                xMax = maxScreenX
                theOtherDimension = trunc((xMax - xMin) / boundingBoxRatio)
                yMin = 0
                yMax = yMin + theOtherDimension

            else:
                # We need to scale from the height
                yMax = maxScreenY
                yMin = 0
                theOtherDimension = trunc((yMax - yMin) * boundingBoxRatio)
                xMin = trunc((maxScreenX - theOtherDimension) / 2)
                xMax = xMin + theOtherDimension
        self.screenX = xMax - xMin
        self.screenY = yMax - yMin

    # this function sets up the canvas and let the measurement start
    def start(self):
        if self.connected:
            # the canvas is created and all elements initialisated
            self.roomSize = self.demoKit.getRoomSize()
            self.defineCanvas()
            self.master = Tk()
            self.master.title("Kinsei Thermal Map Demo: " + self.ip)

            # bind escape to terminate
            self.master.bind('<Escape>', quit)

            # set the common variable background values
            self.canvas = Canvas(self.master, width=(self.screenX + 2 * offset), height=(self.screenY + 2 * offset))
            self.canvas.pack()
            self.realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
            self.thermalMapSettings = self.demoKit.getThermalMapResolution()
            self.grid = self.canvas.grid(row=0, column=0)
            self.drawBackground()

            if showColorMapping:
                self.drawMapColor()
            else:
                self.drawMapTemps()
            self.master.mainloop()

    # draw background
    def drawBackground(self):
        self.canvas.create_rectangle(10, 10, self.screenX + offset, self.screenY + offset, dash=(5, 5), outline="red",
                                     width='2')
        self.canvas.create_polygon(*self.realVertex, fill='', outline='blue', width='2')
        roomSizeLabel = self.canvas.create_text(offset + 5, offset + 5, anchor="nw", font=('Helvetica', 14))
        label = "Room envelop is " + str(int(self.roomSize[0] / 10)) + "cm x " + str(int(self.roomSize[1] / 10)) + "cm"
        self.canvas.itemconfig(roomSizeLabel, text=label)
        if showAverageTemp:
            avgTempLabel = self.canvas.create_text(self.screenX, offset + 5, anchor="ne", font=('Helvetica', 14))
            labelTemp = "Average Temperature is " + "{0:.2f}".format(self.averageTemp) + "C"
            self.canvas.itemconfig(avgTempLabel, text=labelTemp)

    # executes the thermal map with colors
    def drawMapColor(self):
        self.canvas.delete("all")
        w = self.screenX
        h = self.screenY
        pixelTemperatures10 = self.demoKit.getThermalMapPixels()
        if showAverageTemp:
            self.averageTemp = mean(filter(lambda a: a != 0, pixelTemperatures10)) / 10
        if self.coloring == colormaps.matplotlibScaleAdapted:
            frameMax = max(pixelTemperatures10)
            frameMin = min(filter(lambda a: a != 0, pixelTemperatures10))
            colors = [self.coloring(x, frameMin, frameMax) for x in pixelTemperatures10]
        else:
            colors = list(map(self.coloring, pixelTemperatures10))

        # draws the map
        cellwidth = w / self.thermalMapSettings[0]
        cellheight = h / self.thermalMapSettings[1]
        for row in range(self.thermalMapSettings[1]):
            for col in range(self.thermalMapSettings[0]):
                self.canvas.create_rectangle(col * cellwidth + offset, row * cellheight + offset,
                                             (col + 1) * cellwidth + offset, (row + 1) * cellheight + offset,
                                             fill=colors[row * self.thermalMapSettings[0] + col], outline="")

        self.drawBackground()
        self.canvas.after(10, self.drawMapColor)  # delay must be larger than 0

    # executes the thermal map with temperatures
    def drawMapTemps(self):
        self.canvas.delete("all")
        w = self.screenX
        h = self.screenY
        pixelTemperatures10 = self.demoKit.getThermalMapPixels()
        if showAverageTemp:
            self.averageTemp = mean(filter(lambda a: a != 0, pixelTemperatures10)) / 10

        # draws the map
        cellwidth = w / self.thermalMapSettings[0]
        cellheight = h / self.thermalMapSettings[1]
        for row in range(self.thermalMapSettings[1]):
            for col in range(self.thermalMapSettings[0]):
                if pixelTemperatures10[row * self.thermalMapSettings[0] + col] == 0:
                    outlineColor = ""
                else:
                    outlineColor = "gray"
                    if showAverageTemp:
                        colorText = colormaps.threeWayColor(
                            pixelTemperatures10[row * self.thermalMapSettings[0] + col] / 10, self.averageTemp, \
                            minVariation)
                    else:
                        colorText = "black"
                    tempLabelPosition = self.canvas.create_text((col + 0.5) * cellwidth + offset,
                                                                (row + 0.5) * cellheight + offset, anchor="center", \
                                                                font=('Helvetica', 10), fill=colorText)
                    tempLabel = str(pixelTemperatures10[row * self.thermalMapSettings[0] + col] / 10)
                    self.canvas.itemconfig(tempLabelPosition, text=tempLabel)
                self.canvas.create_rectangle(col * cellwidth + offset, row * cellheight + offset,
                                             (col + 1) * cellwidth + offset, (row + 1) * cellheight + offset,
                                             fill="", outline=outlineColor)

        self.drawBackground()
        self.canvas.after(10, self.drawMapTemps)  # delay must be larger than 0


def start():
    root = Tk()
    device = ThermalMap()
    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__":
    start()
