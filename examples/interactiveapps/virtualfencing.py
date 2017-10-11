#!/usr/bin/python3

"""virtualfencing.py: allows to track people, define interest zones, events and monitor them """

from tkinter import *
from math import *
import os
from threading import Lock

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')

import KinseiClient
import gui

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in development"
__requiredfirmware__ = "february2017 or later"

# the color array is used to simplify color assignment to the tracking balls
colors = ["green", "blue", "magenta", "white", "cyan", "black", "yellow", "red"]

# set the viewing window
SCALEX = 0.7  # scale from maximum X size of screen window
SCALEY = 0.7  # scale from maximum X size of screen window
offset = 10  # padding offset in pixels

# set diameter person in pixels
diameter = 20


# this is the main windows whosing tracking, zones, events and control buttons
class MainWindow:
    def __init__(self, maximumSize):
        self.demoKit = None
        self.connected = False
        self.canvas = None
        self.spaceEnvelop = None
        self.master = None
        self.realVertex = None
        self.deviceVertex = None
        self.persons = []
        self.positionData = None
        self.screenX = maximumSize[0]
        self.screenY = maximumSize[1]
        self.counterLabel = None
        self.run = None
        self.ip = None
        self.offset = [offset, offset]
        self.boundary = None
        self.geometry = None
        self.leftLabel = None
        # this lock is betweeb resize and tracking, and it is redundant but left for future changes in the ref module
        self.lock = Lock()

    def connect(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
            self.ip = ip
        except:
            self.connected = False
        # self.ip = "0"
        # self.connected = True

    def isConnected(self):
        return self.connected

    # the KinseiClient class provides coordinates in mm and absolute
    # here we scale to cm and made them relative to our 800x800 canvas
    def adjustedCoordinates(self, coordinates):

        coordX = int((coordinates[0] / 10) * ((self.screenX * 10) / self.spaceEnvelop[0])) + self.offset[0]
        coordY = int((coordinates[1] / 10) * ((self.screenY * 10) / self.spaceEnvelop[1])) + self.offset[1]
        return [coordX, coordY]

    # adjust the canvas dynamically depending on the windows soze
    def defineDynamicCanvas(self, maxWidthOrig, maxHeightOrig):

        boundingBoxRatio = self.spaceEnvelop[0] / self.spaceEnvelop[1]
        maxWidth = maxWidthOrig - 2 * offset
        maxHeight = maxHeightOrig - 2 * offset
        screenRatio = maxWidth / maxHeight
        if screenRatio < 1:
            # portrait screen
            if (boundingBoxRatio < 1) and (screenRatio > boundingBoxRatio):
                # We need to scale from the height
                yMax = maxHeight
                yMin = 0
                theOtherDimension = trunc((yMax - yMin) * boundingBoxRatio)
                xMin = trunc((maxWidth - theOtherDimension) / 2)
                xMax = xMin + theOtherDimension
            else:
                # We need to scale from the width
                xMin = 0
                xMax = maxWidth
                theOtherDimension = trunc((xMax - xMin) / boundingBoxRatio)
                yMin = 0
                yMax = yMin + theOtherDimension
        else:
            # landscape screen
            if (boundingBoxRatio > 1) and (screenRatio < boundingBoxRatio):
                # We need to scale from the width
                xMin = 0
                xMax = maxWidth
                theOtherDimension = trunc((xMax - xMin) / boundingBoxRatio)
                yMin = 0
                yMax = yMin + theOtherDimension

            else:
                # We need to scale from the height
                yMax = maxHeight
                yMin = 0
                theOtherDimension = trunc((yMax - yMin) * boundingBoxRatio)
                xMin = trunc((maxWidth - theOtherDimension) / 2)
                xMax = xMin + theOtherDimension
        screenX = xMax - xMin
        screenY = yMax - yMin
        self.offset[0] = (maxWidthOrig - screenX) / 2
        self.offset[1] = (maxHeightOrig - screenY) / 2
        return [screenX, screenY]

    # this function set-up the canvas and let the tracking start
    def start(self):

        if self.connected:
            # the canvas is created and all elements initialisated
            self.spaceEnvelop = self.demoKit.getRoomSize()
            [self.screenX, self.screenY] = self.defineDynamicCanvas(self.screenX, self.screenY)  # test HERE
            self.offset = [offset, offset]
            self.master = Tk()
            self.master.title("Virtual Fencing Demo: " + self.ip)

            # create the function buttons
            self.create_buttons()

            # creates canvas
            self.canvas = Canvas(self.master, width=(self.screenX + 2 * offset), height=(self.screenY + 2 * offset),
                                 highlightthickness=0)
            self.canvas.pack(fill=BOTH, expand=YES)

            # define starting values and inizial canvas state
            self.deviceVertex = self.demoKit.getRoomCorners()
            self.positionData = self.demoKit.getPersonsPositions()
            self.drawRoomSpace()
            self.drawLabels()
            self.drawPersons()

            # bind escape to terminate
            self.master.bind('<Escape>', quit)

            # bind the window resize to on_resize (not working)
            self.canvas.bind("<Configure>", self.on_resize)

            # the following method starts the tracking
            self.trackPersons()
            self.master.mainloop()

    # execute the redrawing needed for resizing the windows when stretched
    def on_resize(self, event):
        self.lock.acquire()
        [self.screenX, self.screenY] = self.defineDynamicCanvas(event.width, event.height)
        self.drawRoomSpace()
        self.drawLabels()
        self.drawPersons()
        self.lock.release()

    # draws persons on the canvas
    def drawPersons(self):
        if self.positionData:
            newPersons = []
            for i in range(0, len(self.positionData)):
                if self.persons:
                    self.canvas.delete(self.persons[i])
                currentPositionData = self.adjustedCoordinates(self.positionData[i])
                if currentPositionData[0] <= 20 and currentPositionData[1] <= 20:
                    state = HIDDEN
                else:
                    state = NORMAL
                person = self.canvas.create_oval(currentPositionData[0],
                                                 currentPositionData[1],
                                                 currentPositionData[0] + diameter,
                                                 currentPositionData[1] + diameter, fill=colors[i % len(colors)],
                                                 state=state)
                newPersons.append(person)
            self.persons = newPersons

    # draws room walls and envelop on canvas
    def drawRoomSpace(self):
        # fix behaviour on pause!!
        if self.boundary:
            self.canvas.delete(self.boundary)
        self.boundary = self.canvas.create_rectangle(self.offset[0], self.offset[1], self.offset[0] + self.screenX,
                                                     self.screenX + self.offset[1],
                                                     dash=(5, 5), outline="red", width='2')
        if self.geometry:
            self.canvas.delete(self.geometry)
        # testData = [[0, 0], [0, 4000], [4000, 4000], [4000, 0]]
        # self.realVertex = list(map(self.adjustedCoordinates, testData))
        if self.run['text'] == "RUNNING":
            self.realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
        else:
            self.realVertex = list(map(self.adjustedCoordinates, self.deviceVertex))
        self.geometry = self.canvas.create_polygon(*self.realVertex, fill='', outline='blue', width='2')

    # draws labels on canvas
    def drawLabels(self):
        if self.leftLabel:
            self.canvas.delete(self.leftLabel)
        label = "Room envelop is {0}cm x {1}cm".format(str(int(self.spaceEnvelop[0] / 10)), str(
            int(self.spaceEnvelop[1] / 10)))
        self.leftLabel = self.canvas.create_text(self.offset[0] + offset, self.offset[1] + offset, anchor="nw",
                                                 font=('Helvetica', 14))
        self.canvas.itemconfig(self.leftLabel, text=label)
        personFloat = self.demoKit.getNumberPersonsFloat(False)
        personFix = self.demoKit.getNumberPersonsFixed(False)
        # personFloat = 0
        # personFix = 0
        if self.counterLabel:
            self.canvas.delete(self.counterLabel)
        self.counterLabel = self.canvas.create_text(self.offset[0] + self.screenX - offset, self.offset[1] + offset,
                                                    anchor="ne", font=('Helvetica', 14))
        labelCounter = "Number of people: [{0}, {1}]".format("{0:.2f}".format(personFloat), str(personFix))
        self.canvas.itemconfig(self.counterLabel, text=labelCounter)

    # track persons and draw on canvas
    def trackPersons(self):
        if not self.lock.locked():
            if self.run['text'] == "RUNNING":
                self.positionData = self.demoKit.getPersonsPositions()
                personFloat = self.demoKit.getNumberPersonsFloat(False)
                personFix = self.demoKit.getNumberPersonsFixed(False)
                labelCounter = "Number of people: [" + "{0:.2f}".format(personFloat) + ", " + \
                               str(personFix) + "]"
                self.canvas.itemconfig(self.counterLabel, text=labelCounter)
                self.drawPersons()

        self.canvas.after(10, self.trackPersons)  # delay must be larger than 0

    # create all buttons on main window
    def create_buttons(self):
        frame = Frame(self.master, bg='grey', width=400, height=40)
        frame.pack(fill='x')
        # button1 = Button(frame, text='test1')
        # button1.pack(side='left')
        # button2 = Button(frame, text='test2')
        # button2.pack(side='left')
        self.run = Button(frame, text="RUNNING", command=self.togglePause)
        self.run.pack(side='left')

    # toggle pause butting
    def togglePause(self):
        if self.run['text'] == "RUNNING":
            if not self.demoKit.disconnect():
                self.run['text'] = "PAUSED"
                self.run.config(relief=SUNKEN)
        else:
            if self.demoKit.reconnect():
                self.run['text'] = "RUNNING"
                self.run.config(relief=RAISED)


def start():
    root = Tk()
    global maxScreenX
    global maxScreenY
    maxScreenX = root.winfo_screenwidth() * SCALEX
    maxScreenY = root.winfo_screenheight() * SCALEY
    device = MainWindow([maxScreenX, maxScreenY])

    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__":
    start()
