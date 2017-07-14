#!/usr/bin/python3

"""trackingFusionViewer.py: graphical viewer for persons tracking and fusion (raw data indicating
    a possibe detected person where probability of being a real person is proportional to the color brightness)"""

from tkinter import *
from math import *

sys.path.insert(0, '../../libs')
import KinseiClient
import gui
from colormaps import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.8.2"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "february2017 or later"

# the color array is used to simplify color assignment to the tracking balls
colors = ["green", "blue", "magenta", "white", "cyan", "black", "yellow", "red"]

# set the viewing window
SCALEX = 0.7  # scale from maximum X size of screen window
SCALEY = 0.7  # scale from maximum X size of screen window
offset = 10  # padding offset in pixels


# this class shows how to visualise tracking with tkinter
class TrackingFusionViewer:
    def __init__(self):
        self.demoKit = None
        self.connected = False
        self.canvas = None
        self.roomSize = None
        self.master = None
        self.realVertex = None
        self.persons = []
        self.screenX = 0
        self.screenY = 0
        self.fusionMap = None
        self.numberPersons = [0.0, 0]
        self.counterLabel = None
        self.run = None
        self.invertView = False;
        self.ip = ""

    def connect(self, ip):
        try:
            self.ip = ip
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
            # self.demoKit.setTimeIntervalMS(50) # maximum speed
            self.fusionMap = []
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    def invert(self):
        self.invertView = not self.invertView

    # the KinseiClient class provides coordinates in mm and absolute
    # here we scalte to cm and made them relative to our 800x800 canvas
    def adjustedCoordinates(self, coordinates, bottomup=False):
        if bottomup:
            coordX = ((400 - int(coordinates[0] / 10)) * ((self.screenX * 10) / self.roomSize[0])) + offset
            coordY = ((400 - int(coordinates[1] / 10)) * ((self.screenY * 10) / self.roomSize[1])) + offset
        else:
            coordX = int((coordinates[0] / 10) * ((self.screenX * 10) / self.roomSize[0])) + offset
            coordY = int((coordinates[1] / 10) * ((self.screenY * 10) / self.roomSize[1])) + offset
        return [coordX, coordY]

    def defineCanvas(self):
        boundingBoxRatio = self.roomSize[0] / self.roomSize[1]
        screenRatio = maxScreenX / maxScreenY
        if (screenRatio < 1):
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

    # this function set-up the canvas and let the tracking start
    def start(self):
        if self.connected:
            # the canvas is created and all elements initializated
            self.roomSize = self.demoKit.getRoomSize()
            self.defineCanvas()
            self.master = Tk()
            self.master.title("Kinsei Viewer Demo at " + self.ip)

            # bind escape to terminate
            self.master.bind('<Escape>', quit)

            self.canvas = Canvas(self.master, width=(2 * self.screenX + 3 * offset), height=(self.screenY + 5 * offset))
            self.canvas.pack()
            self.canvas.create_rectangle(offset, offset, self.screenX + offset, self.screenY + offset, dash=(5, 5),
                                         outline="blue")
            self.canvas.create_rectangle(self.screenX + 2 * offset, offset, 2 * self.screenX + 2 * offset,
                                         self.screenY + offset, dash=(5, 5), outline="red")

            titleId1 = self.canvas.create_text(self.screenX / 2 - 7 * offset, self.screenY + 2 * offset, anchor="nw",
                                               font=('Helvetica', 20))
            self.canvas.itemconfig(titleId1, text="Tracking Canvas")
            titleId2 = self.canvas.create_text(self.screenX * 1.5 - 5 * offset, self.screenY + 2 * offset, anchor="nw",
                                               font=('Helvetica', 20))
            self.canvas.itemconfig(titleId2, text="Fusion Canvas")
            self.realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
            self.drawBackground()
            positionData = self.demoKit.getPersonsPositions(False)

            self.persons = []
            for i in range(0, len(positionData)):
                person = self.canvas.create_oval(0, 0, 20, 20, fill=colors[i % len(colors)])
                self.persons.append([person, [0, 0]])

            # the following method starts the tracking
            self.trackPersonsAndFusion()
            self.master.mainloop()

    # draw background
    def drawBackground(self):
        self.canvas.create_polygon(*self.realVertex, fill='', outline='blue', width='2')
        fusionVertex = [[a + self.screenX + offset, b] for [a, b] in self.realVertex]
        self.canvas.create_polygon(*fusionVertex, fill='', outline='blue', width='2')
        roomSizeLabel = self.canvas.create_text(offset + 5, offset + 5, anchor="nw", font=('Helvetica', 14))
        label = "Room envelop is " + str(int(self.roomSize[0] / 10)) + "cm x " + str(int(self.roomSize[1] / 10)) + "cm"
        self.canvas.itemconfig(roomSizeLabel, text=label)
        personFloat = self.demoKit.getNumberPersonsFloat(False)
        personFix = self.demoKit.getNumberPersonsFixed(False)
        self.counterLabel = self.canvas.create_text(self.screenX + 3 * offset, offset + 5, \
                                                    anchor="nw", font=('Helvetica', 14))
        labelCounter = "Number of people: [" + "{0:.2f}".format(personFloat) + ", " + \
                       str(personFix) + "]"
        self.canvas.itemconfig(self.counterLabel, text=labelCounter)
        self.run = Button(self.master, text="RUNNING", command=self.togglePause)
        self.run.pack(side=BOTTOM, padx=0, pady=5)

    # toggle pause
    def togglePause(self):
        if self.run['text'] == "RUNNING":
            if not self.demoKit.disconnect():
                self.run['text'] = "PAUSED"
                self.run.config(relief=SUNKEN)
        else:
            if self.demoKit.reconnect():
                self.run['text'] = "RUNNING"
                self.run.config(relief=RAISED)

    # executes the tracking
    def trackPersonsAndFusion(self):
        if self.run['text'] == "RUNNING":
            positionData = self.demoKit.getPersonsPositions()
            fusionData = self.demoKit.getFusionValues(False)
            personFloat = self.demoKit.getNumberPersonsFloat(False)
            personFix = self.demoKit.getNumberPersonsFixed(False)
            labelCounter = "Number of people: [" + "{0:.2f}".format(personFloat) + ", " + \
                           str(personFix) + "]"
            self.canvas.itemconfig(self.counterLabel, text=labelCounter)

            self.updateFusionMap(fusionData)

            for i in range(0, len(positionData)):
                currentPositionData = self.adjustedCoordinates(positionData[i], self.invertView)
                if currentPositionData == [10, 10]:
                    currentPositionData = [-50, -50]
                deltax = currentPositionData[0] - self.persons[i][1][0]
                deltay = currentPositionData[1] - self.persons[i][1][1]
                self.canvas.move(self.persons[i][0], deltax, deltay)
                self.persons[i][1] = currentPositionData

        self.canvas.after(10, self.trackPersonsAndFusion)  # delay must be larger than 0

    # draw the fusion map
    def updateFusionMap(self, fusionData):
        # clean the current fusion map
        for i in range(0, len(self.fusionMap)):
            self.canvas.delete(self.fusionMap[i])
        self.fusionMap = []
        for i in range(0, len(fusionData)):
            currentPositionData = self.adjustedCoordinates([fusionData[i][0], fusionData[i][1]], self.invertView)
            x0 = currentPositionData[0] + self.screenX + offset
            y0 = currentPositionData[1]
            x1 = currentPositionData[0] + self.screenX + 3 * offset
            y1 = currentPositionData[1] + 2 * offset
            self.fusionMap.append(
                self.canvas.create_oval(x0, y0, x1, y1, fill=colorscale("#ff0000", fusionData[i][2] / 26)))


def start():
    root = Tk()
    global maxScreenX
    global maxScreenY
    maxScreenX = root.winfo_screenwidth() * SCALEX
    maxScreenY = root.winfo_screenheight() * SCALEY
    device = TrackingFusionViewer()
    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__":
    start()
