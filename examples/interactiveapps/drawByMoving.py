#!/usr/bin/python3

"""drawByMoving.py: example of detecting a position to draw lines. It is the basic algorithm needed for defining
entry and exit zones by moving around as well as it has a fun factor to it. Some parameters can be modified via GUI
in order to alter the behaviour """

from tkinter import *
from math import *
import os

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')

import KinseiClient
import gui

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "february2017 or later"

# the color array is used to simplify color assignment to the tracking balls
# change for changing colors
colors = ["green", "blue", "magenta", "cyan", "black", "yellow", "red", "orange"]

# set the viewing window
SCALEX = 0.7  # scale from maximum X size of screen window
SCALEY = 0.7  # scale from maximum X size of screen window
offset = 10  # padding offset in pixels

# programmatic parameters default values
LINEWIDTH = 1       # set the tracking line width
MAXMOVE = 400       # set the maximum line variation (pixels)
FRAMESRATE = 1      # set the periodicity of reading from the device
STABLITYRATE = 3    # set the number of captures frames needed for a position to be stable


# this class shows how to visualise tracking with tkinter
class DrawByMoving:
    def __init__(self):
        self.demoKit = None
        self.connected = False
        self.canvas = None
        self.roomSize = None
        self.master = None
        self.masterFrame = None
        self.realVertex = None
        self.persons = []
        self.screenX = 0
        self.screenY = 0
        self.counterLabel = None
        self.run = None
        self.invertView = False
        self.ip = None
        self.maxFrameRate = 0
        self.trackedPeople = 0

        # programmatic parameters
        self.LINEWIDTH = None           # set the tracking line width
        self.MAXMOVE = None             # set the maximum line lenght (pixels)
        self.FRAMESRATE = None          # set the periodicity of reading from the device
        self.STABILITYRATE = None       # set the number of captures frames needed for a position to be stable
        self.TRACKEDPEOPLE = []         # mask for tracker people

    def connect(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
            self.ip = ip
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    def invert(self):
        self.invertView = not self.invertView

    # the KinseiClient class provides coordinates in mm and absolute
    # here we scale to cm and made them relative to our 800x800 canvas
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

    # this function set-up the canvas and let the tracking start
    def start(self):

        if self.connected:
            # the canvas is created and all elements initialisated
            self.roomSize = self.demoKit.getRoomSize()
            positionData = self.demoKit.getPersonsPositions(False)
            self.trackedPeople = len(positionData)
            self.defineCanvas()
            self.master = Tk()
            self.master.title("Kinsei drawing by movement: " + self.ip)

            # bind escape to terminate
            self.master.bind('<Escape>', quit)

            # set master frame
            self.masterFrame = Frame(self.master)
            self.masterFrame.pack(side=TOP)

            # prepare the tracking canvas frame
            self.setupTrackingCanvas()

            # prepare paramenet frame
            self.setupParameterMenu()
            self.maxFrameRate = self.demoKit.getTimeIntervalMS()
            self.demoKit.setTimeIntervalMS(self.maxFrameRate * self.FRAMESRATE.get())

            # preparing the pause button
            self.run = Button(self.master, text="RUNNING", command=self.togglePause)
            self.run.pack(side=BOTTOM, padx=0, pady=5)

            # drawing initial position markers
            for i in range(0, self.trackedPeople):
                person = self.canvas.create_oval(0, 0, 20, 20, fill=colors[i % len(colors)])
                self.persons.append([person, [0, 0]])

            # the following method starts the tracking
            self.trackPersons()
            self.master.mainloop()

    # setup the tracking canvas
    def setupTrackingCanvas(self):
        canvasFrame = Frame(self.masterFrame, width=(self.screenX + 2 * offset), height=(self.screenY + 2 * offset))
        canvasFrame.pack(expand=1, fill=X, pady=offset, padx=offset, side=LEFT)
        self.canvas = Canvas(canvasFrame, bg='white', width=self.screenX + offset, height=self.screenY + offset)
        self.canvas.pack()
        self.realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
        self.canvas.create_rectangle(10, 10, self.screenX + offset, self.screenY + offset, dash=(5, 5), outline="red",
                                     width='2')
        self.canvas.create_polygon(*self.realVertex, fill='', outline='blue', width='2')
        roomSizeLabel = self.canvas.create_text(offset + 5, offset + 5, anchor="nw", font=('Helvetica', 14))
        label = "Room envelop is " + str(int(self.roomSize[0] / 10)) + "cm x " + str(int(self.roomSize[1] / 10)) + "cm"
        self.canvas.itemconfig(roomSizeLabel, text=label)
        personFloat = self.demoKit.getNumberPersonsFloat(False)
        personFix = self.demoKit.getNumberPersonsFixed(False)
        self.counterLabel = self.canvas.create_text(offset + 5, offset + 25, anchor="nw", font=('Helvetica', 14))
        labelCounter = "Number of people: [" + "{0:.2f}".format(personFloat) + ", " + \
                       str(personFix) + "]"
        self.canvas.itemconfig(self.counterLabel, text=labelCounter)

    # set-up the parametric menu as well as connect it to the proper class variable
    def setupParameterMenu(self):
        #TODO needs to add the stability radius
        paramenetsFrame = Frame(self.masterFrame, width=300, height=(self.screenY + 2 * offset))
        paramenetsFrame.pack(expand=1, fill=X, pady=offset, padx=offset, side=RIGHT)

        frameEntry = Frame(paramenetsFrame)
        frameEntry.pack(padx=20, pady=20)
        frameRadio = Frame(paramenetsFrame)
        frameRadio.pack(padx=20, pady=20)
        frameButtons = Frame(paramenetsFrame)
        frameButtons.pack(padx=20, pady=20)

        self.LINEWIDTH = StringVar(self.master, value=LINEWIDTH)
        self.MAXMOVE = StringVar(self.master, value=MAXMOVE)
        self.FRAMESRATE = StringVar(self.master, value=FRAMESRATE)
        self.STABILITYRATE = StringVar(self.master, value=STABLITYRATE)
        self.STABILITYRADIUS = StringVar(self.master, value=self.demoKit.getStabilityRadius())

        Label(frameEntry, text="Line width").grid(row=0, sticky=E)
        Label(frameEntry, text="Max line length").grid(row=1, sticky=E)
        Label(frameEntry, text="Framerate").grid(row=2, sticky=E)
        Label(frameEntry, text="Stability rate").grid(row=3, sticky=E)
        Label(frameEntry, text="Stability radius").grid(row=4, sticky=E)

        linewidth = Entry(frameEntry, textvariable=self.LINEWIDTH)
        maxmove = Entry(frameEntry, textvariable=self.MAXMOVE)
        framerate = Entry(frameEntry, textvariable=self.FRAMESRATE)
        stabilityrate = Entry(frameEntry, textvariable=self.STABILITYRATE)
        stabilityradius = Entry(frameEntry, textvariable=self.STABILITYRADIUS)
        linewidth.grid(row=0, column=1)
        maxmove.grid(row=1, column=1)
        framerate.grid(row=2, column=1)
        stabilityrate.grid(row=3, column=1)
        stabilityradius.grid(row=4, column=1)

        Label(frameRadio, text="Tracking").grid(row=0, column=0, sticky=E)
        for i in range(0, self.trackedPeople):
            self.TRACKEDPEOPLE.append(IntVar(self.master, value=1))
            Checkbutton(frameRadio, text="person "+str(i), variable=self.TRACKEDPEOPLE[i]).grid(row=i,column=1, sticky=W)

        Button(frameButtons, text='Reset', command=self.resetPArameters).grid(row=0, column=1)

    # reset parameters
    def resetPArameters(self):
        self.LINEWIDTH.set(LINEWIDTH)
        self.MAXMOVE.set(MAXMOVE)
        self.FRAMESRATE.set(FRAMESRATE)
        self.STABILITYRATE.set(STABLITYRATE)

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
    def trackPersons(self):
        stabilityrate = self.STABILITYRATE.get()
        framerate = self.FRAMESRATE.get()
        if framerate != "":
            self.demoKit.setTimeIntervalMS(self.maxFrameRate * int(framerate))

        if self.run['text'] == "RUNNING" and stabilityrate:
            if int(stabilityrate) == 0:
                positionData = self.demoKit.getPersonsPositions()
            else:
                positionData = self.demoKit.getAlStablePositions(int(stabilityrate))
            personFloat = self.demoKit.getNumberPersonsFloat(False)
            personFix = self.demoKit.getNumberPersonsFixed(False)
            labelCounter = "Number of people: [" + "{0:.2f}".format(personFloat) + ", " + \
                           str(personFix) + "]"
            self.canvas.itemconfig(self.counterLabel, text=labelCounter)

            for i in range(0, len(positionData)):
                linewidth = self.LINEWIDTH.get()
                maxmove = self.MAXMOVE.get()
                if positionData[i] and (self.TRACKEDPEOPLE[i].get() == 1) and (linewidth != "") and (maxmove != ""):
                    currentPositionData = self.adjustedCoordinates(positionData[i], self.invertView)
                    if currentPositionData == [10, 10]:
                        currentPositionData = [-50, -50]
                    deltax = currentPositionData[0] - self.persons[i][1][0]
                    deltay = currentPositionData[1] - self.persons[i][1][1]
                    self.canvas.move(self.persons[i][0], deltax, deltay)
                    if (abs(deltax) < int(maxmove)) and (abs(deltay) < int(maxmove)):
                        self.canvas.create_line(self.persons[i][1][0], self.persons[i][1][1], currentPositionData[0],
                                                currentPositionData[1], fill=colors[i % len(colors)],
                                                width=int(linewidth))
                    self.persons[i][1] = currentPositionData

        self.canvas.after(10, self.trackPersons)  # delay must be larger than 0


def start():
    root = Tk()
    global maxScreenX
    global maxScreenY
    maxScreenX = root.winfo_screenwidth() * SCALEX
    maxScreenY = root.winfo_screenheight() * SCALEY
    device = DrawByMoving()
    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__":
    start()
