#!/usr/bin/python3

"""virtualfencing.py: allows to track people, define interest zones, events and monitor them """

from tkinter import *
from math import *
import os
from threading import Lock
import sys
from tkinter import filedialog
from tkinter import messagebox
import platform

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')

import KinseiClient
import gui
from geometry import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.9.4"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "alpha release"
__requiredfirmware__ = "february2017 or later"

# EVENT VARIABLES

## definition of events labels
crossEvents = ['From Left', 'From Right']
rectEvents = ['Is Inside', 'Is Outside', 'Disappear Inside', 'Entering', 'Exiting']
ovalEvents = ['Is Inside', 'Is Outside', 'Disappear Inside', 'Entering', 'Exiting']
polyEvents = ['Is Inside', 'Is Outside', 'Disappear Inside', 'Entering', 'Exiting', 'Crossing']

## definition of basic event flags

fromLeft = 0xb01000000
fromRight = 0xb00100000
isLeft = 0xb10000000 | fromRight
isRight = 0xb10000000 | fromLeft
isInside = 0xb00010000
isOutside = 0xb00001000
disappearing = 0xb00000100
entering = 0xb00000010 | isInside
exiting = 0xb00000001 | isOutside
empty = 0xb00000000

## definition of event flags per type of alarms

crossEventsFlags = [fromLeft, fromRight]
rectEventsFlags = [isInside, isOutside, isInside & disappearing, entering, exiting]
ovalEventsFlags = [isInside, isOutside, isInside & disappearing, entering, exiting]
polyEventsFlags = [isInside, isOutside, isInside & disappearing, entering, exiting, entering & exiting]

# INTERNAL VARIABLES

## Application name
APPNAME = "Installation and Test Deck: "

# theses color arrays are used to simplify color assignments
colorsTracking = ["magenta", "black", "red", "green", "blue", "white", "yellow", "red"]
colorsAlarm = ["red", "yellow", "magenta", "blue", "green"]

# when personMarkerFileVector is set, these images are used in the tracking instead of the fat dots
markerFolder = "./images/"
personMarkerFileVector = ["mario.gif", "donkey_kong.gif", "princess.gif", "bowser_jr.gif", "luigi.gif", "barrel.gif",
                          "mushroom.gif", "turtle.gif"]
# personMarkerFileVector = [] # uncomment to remove image markers and use fat dots

## set the viewing window
SCALEX = 0.7  # scale from maximum X size of screen window
SCALEY = 0.7  # scale from maximum X size of screen window
offset = 10  # padding offset in pixels

## set diameter person in pixels
diameter = 20

## set selection distance in pixels
nearbyDistance = 5

## programmatic parameters default values
LINEWIDTH = 1  # set the tracking line width
MAXMOVE = 400  # set the maximum line variation (pixels)
FRAMESRATE = 1  # set the periodicity of reading from the device
STABLITYRATE = 3  # set the number of captures frames needed for a position to be stable

## alarm presets
PERSISTANCE = 3  # number of frames

## element coloring
ROOMBACKGROUND = 'PaleTurquoise1'
ROOMWALLS = 'black'
WALLTHICKNESS = '4'
ENVELOPTHICKNESS = '1'
ALARMBACKGROUND = 'white'


# this is the main windows whosing tracking, zones, alarms, events and control buttons
class MainWindow:
    def __init__(self, maximumSize):

        # device
        self.demoKit = None
        self.connected = False
        self.ip = None

        # main canvas
        self.canvas = None
        self.spaceEnvelop = None
        self.master = None
        self.realVertex = None
        self.deviceVertex = None
        self.persons = []
        self.positionData = None
        self.personMarkers = []
        self.screenX = maximumSize[0]
        self.screenY = maximumSize[1]
        self.counterLabel = None
        self.offset = [offset, offset]
        self.boundary = None
        self.geometry = None
        self.leftLabel = None
        self.multiplierMmPx = 1
        # this lock is betweeb resize and tracking, and it is redundant but left for future changes in the ref module
        self.lock = Lock()

        # MENU CONTROL
        self.extraWindows = []

        # RUNNING
        self.run = None

        # TRACING
        self.tracing = None
        self.traceWin = None
        self.LINEWIDTH = None  # set the tracking line width
        self.MAXMOVE = None  # set the maximum line lenght (pixels)
        self.FRAMESRATE = None  # set the periodicity of reading from the device
        self.STABILITYRATE = None  # set the number of captures frames needed for a position to be stable
        self.TRACKEDPEOPLE = []  # mask for tracker people
        self.STABILITYRADIUS = None
        self.traceLines = []  # drawn lines
        self.traceLinesCoords = []  # drawn lines
        self.lineParameters = []  # store the line width and maxmove

        # ZONES menus

        # ALARMS definition
        self.alarms = None
        self.canvasAlarm = []
        self.pointerLine = None
        self.canvasItems = []
        self.activeAction = Lock()

        # EVENT monitor
        self.monitor = None
        self.monitorActive = Lock()
        self.eventStatus = []

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

    # adjusts the coordinates in mm to screen values
    def adjustedCoordinates(self, coordinates):

        coordX = int((coordinates[0] / 10) * ((self.screenX * 10) / self.spaceEnvelop[0])) + self.offset[0]
        coordY = int((coordinates[1] / 10) * ((self.screenY * 10) / self.spaceEnvelop[1])) + self.offset[1]
        return [coordX, coordY]

    # extracts the coordinates in mm from screen values
    def extractCoordinates(self, coordinates):

        coordX = (coordinates[0] - self.offset[0]) * (self.spaceEnvelop[0] / (self.screenX * 10)) * 10
        coordY = (coordinates[1] - self.offset[1]) * (self.spaceEnvelop[1] / (self.screenY * 10)) * 10
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
        self.multiplierMmPx = self.spaceEnvelop[0] / screenX
        return [screenX, screenY]

    # this function set-up the canvas and let the tracking start
    def start(self):

        if self.connected:
            # the canvas is created and all elements initialisated
            self.spaceEnvelop = self.demoKit.getRoomSize()
            [self.screenX, self.screenY] = self.defineDynamicCanvas(self.screenX, self.screenY)
            self.offset = [offset, offset]
            self.master = Tk()
            self.master.title(APPNAME + self.ip)

            # cerate menus
            self.create_menu()

            # create the function buttons
            self.create_buttons()

            # creates canvas
            self.canvas = Canvas(self.master, width=(self.screenX + 2 * offset), height=(self.screenY + 2 * offset),
                                 highlightthickness=0)
            self.canvas.pack(fill=BOTH, expand=YES)
            self.canvas.configure(background='white')

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
        self.scaleTracingLines()
        self.scaleAlarmDrawing()
        self.lock.release()

    # scale tracing lines
    def scaleTracingLines(self):

        def drawVector(currentVector, previousVector):
            for j in range(0, len(currentVector)):

                if previousVector[j][0] > 0 and previousVector[j][1] > 0 and currentVector[j][0] > 0 \
                        and currentVector[j][1] > 0:
                    previousPositionData = self.adjustedCoordinates(previousVector[j])
                    currentPositionData = self.adjustedCoordinates(currentVector[j])
                    deltax = currentPositionData[0] - previousPositionData[0]
                    deltay = currentPositionData[1] - previousPositionData[1]
                    if (abs(deltax) < int(maxmove)) and (abs(deltay) < int(maxmove)):
                        line = self.canvas.create_line(previousPositionData[0], previousPositionData[1],
                                                       currentPositionData[0], currentPositionData[1],
                                                       fill=colorsTracking[j % len(colorsTracking)],
                                                       width=int(linewidth))
                        self.traceLines.append(line)

        if self.traceLines:
            for line in self.traceLines:
                self.canvas.delete(line)
            for i in range(1, len(self.traceLinesCoords)):
                linewidth = self.lineParameters[i][0]
                maxmove = self.lineParameters[i][1]
                currentVector = self.traceLinesCoords[i]
                previousVector = self.traceLinesCoords[i - 1]
                drawVector(currentVector, previousVector)
            drawVector(self.traceLinesCoords[0], self.traceLinesCoords[-1])

    # draws persons on the canvas
    def drawPersons(self):
        if self.positionData:
            newPersons = []
            if personMarkerFileVector:
                if not self.personMarkers:
                    # initialise the marker image vector
                    for i in range(0, len(self.positionData)):
                        imageIndex = i % len(personMarkerFileVector)
                        fileImage = markerFolder + personMarkerFileVector[imageIndex]
                        self.personMarkers.append(PhotoImage(file=fileImage))
                    pass
                # use markers
                for i in range(0, len(self.positionData)):
                    if self.persons:
                        if self.persons[i]:
                            self.canvas.delete(self.persons[i])
                    currentPositionData = self.adjustedCoordinates(self.positionData[i])
                    if self.positionData[i][0] <= 20 and self.positionData[i][1] <= 20:
                        person = None
                    else:
                        person = self.canvas.create_image(currentPositionData[0], currentPositionData[1],
                                                          image=self.personMarkers[i])
                    # person = self.canvas.create_image(currentPositionData[0],currentPositionData[1],image=self.personMarkers[i])
                    newPersons.append(person)
            else:
                for i in range(0, len(self.positionData)):
                    if self.persons:
                        self.canvas.delete(self.persons[i])
                    currentPositionData = self.adjustedCoordinates(self.positionData[i])
                    if self.positionData[i][0] <= 20 and self.positionData[i][1] <= 20:
                        state = HIDDEN
                    else:
                        state = NORMAL
                    person = self.canvas.create_oval(currentPositionData[0],
                                                     currentPositionData[1],
                                                     currentPositionData[0] + diameter,
                                                     currentPositionData[1] + diameter,
                                                     fill=colorsTracking[i % len(colorsTracking)],
                                                     state=state)
                    newPersons.append(person)
            self.persons = newPersons

    # draws tracing lines
    def drawTracingLines(self):
        if 1 in map(IntVar.get, self.TRACKEDPEOPLE):
            newPositionVector = []
            linewidth = self.LINEWIDTH.get()
            if not linewidth:
                linewidth = LINEWIDTH
            maxmove = self.MAXMOVE.get()
            if not maxmove:
                maxmove = MAXMOVE
            self.lineParameters.append([linewidth, maxmove])
            for i in range(0, len(self.positionData)):
                if self.TRACKEDPEOPLE[i].get():
                    newPositionVector.append(self.positionData[i])
                    if len(self.traceLinesCoords) > 0:
                        if self.traceLinesCoords[-1][i][0] > 0 and self.traceLinesCoords[-1][i][1] > 0 \
                                and self.positionData[i][0] > 0 and self.positionData[i][1] > 0:
                            previousPositionData = self.adjustedCoordinates(self.traceLinesCoords[-1][i])
                            currentPositionData = self.adjustedCoordinates(self.positionData[i])
                            deltax = currentPositionData[0] - previousPositionData[0]
                            deltay = currentPositionData[1] - previousPositionData[1]
                            if (abs(deltax) < int(maxmove)) and (abs(deltay) < int(maxmove)):
                                line = self.canvas.create_line(previousPositionData[0], previousPositionData[1],
                                                               currentPositionData[0], currentPositionData[1],
                                                               fill=colorsTracking[i % len(colorsTracking)],
                                                               width=int(linewidth))
                                self.traceLines.append(line)
                else:
                    newPositionVector.append([0, 0])
            self.traceLinesCoords.append(newPositionVector)

    # draws room walls and envelop on canvas
    def drawRoomSpace(self):
        # fix behaviour on pause!!
        if self.boundary:
            self.canvas.delete(self.boundary)
        self.boundary = self.canvas.create_rectangle(self.offset[0], self.offset[1], self.offset[0] + self.screenX,
                                                     self.screenX + self.offset[1],
                                                     dash=(5, 5), outline="red", width=ENVELOPTHICKNESS)
        if self.geometry:
            self.canvas.delete(self.geometry)
        if self.run['text'] == "RUNNING":
            self.realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
        else:
            self.realVertex = list(map(self.adjustedCoordinates, self.deviceVertex))
        self.geometry = self.canvas.create_polygon(*self.realVertex, fill=ROOMBACKGROUND, outline=ROOMWALLS,
                                                   width=WALLTHICKNESS)

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
                self.drawTracingLines()
                if self.monitorActive.locked():
                    self.monitorForEvents()
                else:
                    pass

        self.canvas.after(10, self.trackPersons)  # delay must be larger than 0

    # define the menu and associated elements
    def create_menu(self):
        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load Alarms", command=self.loadAlarms)
        filemenu.add_command(label="Save Alarms", command=self.saveAlarms)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

    def saveAlarms(self):
        self.master.filename = filedialog.asksaveasfilename(initialdir="./", title="Select file",
                                                            filetypes=(("alarm files", "*.alm"), ("all files", "*.*")))
        if platform.system() != 'Linux' or platform.system() == 'Windows':
            self.master.filename += ".alm"
        with (open(self.master.filename, 'w')) as saveFile:
            for event in self.canvasAlarm:
                saveFile.write(event[0] + ";")
                for coords in event[1]:
                    saveFile.write(" ")
                    saveFile.write(str(coords[0]) + " ")
                    saveFile.write(str(coords[1]))
                saveFile.write(";")
                try:
                    for el in event[2]:
                        saveFile.write(" ")
                        saveFile.write(str(el))
                except:
                    saveFile.write(" ")
                    saveFile.write(str(event[2]))
                saveFile.write(";")
                for coords in event[3]:
                    saveFile.write(" ")
                    saveFile.write(str(coords[0]) + " ")
                    saveFile.write(str(coords[1]))
                saveFile.write("; ")
                saveFile.write(event[4] + "; ")
                saveFile.write(str(event[5]) + "; ")
                saveFile.write(event[6] + ";")
                saveFile.write("\n")

    def loadAlarms(self):
        self.master.filename = filedialog.askopenfilename(initialdir="./", title="Select file",
                                                          filetypes=(("alarm files", "*.alm"), ("all files", "*")))
        try:
            if self.master.filename:
                for alarm in self.canvasAlarm:
                    self.canvas.delete(alarm[2])
                self.canvasAlarm = []
                with (open(self.master.filename, 'r')) as loadFile:
                    for line in loadFile:
                        linedata = line.split(';')[0:-1]
                        alarm = [linedata[0]]
                        coord = list(map(int, linedata[1].strip().split(' ')))
                        coordList = []
                        for i in range(0, len(coord) // 2):
                            point = [coord[2 * i], coord[1 + 2 * i]]
                            coordList.append(point)
                        alarm.append(coordList)
                        elements = list(map(int, linedata[2].strip().split(' ')))
                        if len(elements) == 1:
                            alarm.append(elements[0])
                        else:
                            alarm.append(elements)
                        coord = list(map(float, linedata[3].strip().split(' ')))
                        coordList = []
                        for i in range(0, len(coord) // 2):
                            point = [coord[2 * i], coord[1 + 2 * i]]
                            coordList.append(point)
                        alarm.append(coordList)
                        alarm.append(linedata[4].strip())
                        alarm.append(int(linedata[5].strip()))
                        alarm.append(linedata[6].strip())
                        self.canvasAlarm.append(alarm)

                self.monitorWindowToggle(True)
                self.scaleAlarmDrawing()
                self.eventStatus = []
        except:
            messagebox.showerror("Answer", "Invalid file")

    # create all buttons on main window
    def create_buttons(self):
        frame = Frame(self.master, bg='grey', width=400, height=40)
        frame.pack(fill='x')
        self.run = Button(frame, text="RUNNING", command=self.togglePause)
        self.run.pack(side='left')
        self.tracing = Button(frame, text="TRACING", command=self.traceTrackingLauncher)
        self.tracing.pack(side='left')
        # self.monitor = Button(frame, text="ZONES")
        # self.monitor.pack(side='left')
        self.alarms = Button(frame, text="ALARMS", command=self.alarmWindowLancher)
        self.alarms.pack(side='left')
        self.monitor = Button(frame, text="MONITOR OFF", command=self.monitorWindowToggle)
        self.monitor.pack(side='left')

    # RUNNING menu

    ## execute the start and pause fanction
    def togglePause(self):
        if self.run['text'] == "RUNNING":
            if not self.demoKit.disconnect():
                self.run['text'] = "PAUSED"
                self.run.config(relief=SUNKEN)
        else:
            if self.demoKit.reconnect():
                self.run['text'] = "RUNNING"
                self.run.config(relief=RAISED)

    # TRACING menu
    def traceTrackingLauncher(self):

        ## set up the tracing window
        def tracingwindow():
            master = self.traceWin
            master.title("Tracing menu")

            # bind escape to terminate
            master.bind('<Escape>', quit)

            canvas = Canvas(master)
            canvas.pack(fill=BOTH, expand=1)

            frameEntry = Frame(canvas)
            frameEntry.pack(padx=20, pady=20)
            frameRadio = Frame(canvas)
            frameRadio.pack(padx=20, pady=20)
            frameButtons = Frame(canvas)
            frameButtons.pack(padx=20, pady=20)

            self.LINEWIDTH = StringVar(self.master, value=LINEWIDTH)
            self.MAXMOVE = StringVar(self.master, value=MAXMOVE)
            self.FRAMESRATE = StringVar(self.master, value=FRAMESRATE)
            self.STABILITYRATE = StringVar(self.master, value=STABLITYRATE)
            self.STABILITYRADIUS = StringVar(self.master, value=self.demoKit.getStabilityRadius())

            linewidth = Label(frameEntry, text="Line width")
            maxmove = Label(frameEntry, text="Max line length")
            framerate = Label(frameEntry, text="Framerate")
            srate = Label(frameEntry, text="Stability rate")
            srateradius = Label(frameEntry, text="Stability radius")

            linewidth.grid(row=0, sticky=E)
            maxmove.grid(row=1, sticky=E)
            framerate.grid(row=2, sticky=E)
            srate.grid(row=3, sticky=E)
            srateradius.grid(row=4, sticky=E)

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

            Label(frameRadio, text="Tracing").grid(row=0, column=0, sticky=E)
            for i in range(0, len(self.persons)):
                self.TRACKEDPEOPLE.append(IntVar(self.master, value=0))
                Checkbutton(frameRadio, text="person " + str(i), variable=self.TRACKEDPEOPLE[i]).grid(row=i, column=1,
                                                                                                      sticky=W)

            Button(frameButtons, text='Reset', command=self.resetParameters).grid(row=0, column=1)
            Button(frameButtons, text='Empty', command=self.removeLines).grid(row=0, column=0)

        if "traceTracking" not in self.extraWindows:
            self.extraWindows.append("traceTracking")
            self.traceWin = Toplevel()
            tracingwindow()
        else:
            try:
                self.traceWin.state()
            except:
                self.traceWin = Toplevel()
                tracingwindow()

    ## removes all lines from the canvas
    def removeLines(self):
        if self.traceLines:
            self.traceLinesCoords = []
            self.linewidth = []
            for line in self.traceLines:
                self.canvas.delete(line)

    ## reset parameters
    def resetParameters(self):
        self.LINEWIDTH.set(LINEWIDTH)
        self.MAXMOVE.set(MAXMOVE)
        self.FRAMESRATE.set(FRAMESRATE)
        self.STABILITYRATE.set(STABLITYRATE)

    # ALARMS menu

    ## alarm window menu launcher
    def alarmWindowLancher(self):
        if "alarms" not in self.extraWindows:
            self.extraWindows.append("alarms")
            self.traceWin = Toplevel()
            self.alarmWindow()
        else:
            try:
                self.traceWin.state()
            except:
                self.traceWin = Toplevel()
                self.alarmWindow()

    ## set up the alarm menu and actions
    def alarmWindow(self):

        # gui canvas
        master = self.traceWin
        master.title("Alarm menu")
        canvas = Canvas(master)
        canvas.pack(fill=BOTH, expand=1)
        frameButtons = Frame(canvas)
        frameEntry = Frame(canvas)
        frameRadio = Frame(canvas)
        frameColors = Frame(canvas)
        frameData = Frame(canvas)

        def defineActionMenuCross():
            defineActionMenu('cross', crossEvents)

        def defineActionMenuRect():
            defineActionMenu('rect', rectEvents)

        def defineActionMenuOval():
            defineActionMenu('oval', ovalEvents)

        def defineActionMenuPoly():
            defineActionMenu('poly', polyEvents)

        def defineActionMenu(typeAction, labelDir):

            drawingPoints = []
            eventRadio = []
            colorRadio = []
            actionLabel.config(text=typeAction)
            # stabilityTimeVar = StringVar(master, value=FRAMESRATE)
            stabilityTimeVar = StringVar(master, value=" ! not used yet !")
            stabilityTimeLabel = Label(frameEntry, text="Stability time ms")
            stabilityTimeLabel.grid(row=0, sticky=E)
            stabilityTime = Entry(frameEntry, textvariable=stabilityTimeVar)
            stabilityTime.grid(row=0, column=1)
            alarmType = StringVar()
            alarmColor = StringVar()

            for i in range(0, len(labelDir)):
                eventRadio.append(
                    Radiobutton(frameRadio, text=labelDir[i], variable=alarmType, value=labelDir[i], indicatoron=0,
                                selectcolor='gray'))
                eventRadio[i].grid(row=0, column=i)

            for i in range(0, len(colorsAlarm)):
                colorRadio.append(
                    Radiobutton(frameColors, text=colorsAlarm[i], variable=alarmColor, value=colorsAlarm[i],
                                indicatoron=0, selectcolor='gray'))
                colorRadio[i].grid(row=0, column=i)

            alarmType.set(labelDir[0])
            alarmColor.set(colorsAlarm[0])

            def defineAction(event):
                try:
                    if not self.lock.locked():
                        if isPointInPoly([event.x, event.y], self.realVertex):
                            drawingPoints.append([event.x, event.y])
                        if len(drawingPoints) == 2 and typeAction != 'poly':
                            if typeAction == 'cross':
                                self.canvasItems.append(
                                    self.canvas.create_line(drawingPoints[0][0], drawingPoints[0][1],
                                                            drawingPoints[1][0], drawingPoints[1][1],
                                                            dash=(3, 5), width=1))
                            elif typeAction == 'rect':
                                self.canvasItems.append(
                                    self.canvas.create_rectangle(drawingPoints[0][0], drawingPoints[0][1],
                                                                 drawingPoints[1][0], drawingPoints[1][1],
                                                                 dash=(3, 5), width=1, fill=ALARMBACKGROUND))
                            elif typeAction == 'oval':
                                self.canvasItems.append(
                                    self.canvas.create_oval(drawingPoints[0][0], drawingPoints[0][1],
                                                            drawingPoints[1][0], drawingPoints[1][1],
                                                            dash=(3, 5), width=1, fill=ALARMBACKGROUND))
                            self.canvas.unbind("<Motion>", bindIDmove)
                            self.canvas.unbind("<Button-2>", bindIDclick)
                            actionEvent(drawingPoints)
                            if self.pointerLine:
                                self.canvas.delete(self.pointerLine)
                            self.activeAction.release()
                        elif len(drawingPoints) > 1 and typeAction == 'poly':
                            self.canvasItems.append(self.canvas.create_line(drawingPoints[-2][0], drawingPoints[-2][1],
                                                                            drawingPoints[-1][0], drawingPoints[-1][1],
                                                                            dash=(3, 5), width=1))
                            if self.pointerLine:
                                self.canvas.delete(self.pointerLine)
                except:
                    forceUnlock()

            def traceAction(event):
                try:
                    cmDistance = 0
                    if len(drawingPoints) >= 1:
                        if self.pointerLine:
                            self.canvas.delete(self.pointerLine)
                        if typeAction == 'cross':
                            cmDistance = int(
                                self.multiplierMmPx * distancePoint(drawingPoints[-1], [event.x, event.y]) / 10)
                            self.pointerLine = self.canvas.create_line(drawingPoints[0][0], drawingPoints[0][1],
                                                                       event.x, event.y, dash=(3, 5), width=1)
                        elif typeAction == 'rect':
                            cmDistance = [int(abs(self.multiplierMmPx * (drawingPoints[-1][0] - event.x) / 10)),
                                          int(abs(self.multiplierMmPx * (drawingPoints[-1][1] - event.y) / 10))]
                            self.pointerLine = self.canvas.create_rectangle(drawingPoints[0][0], drawingPoints[0][1],
                                                                            event.x, event.y, dash=(3, 5), width=1)
                        elif typeAction == 'oval':
                            cmDistance = int(abs(self.multiplierMmPx * (drawingPoints[-1][0] - event.x) / 20))
                            self.pointerLine = self.canvas.create_oval(drawingPoints[0][0], drawingPoints[0][1],
                                                                       event.x, event.y, dash=(3, 5), width=1)
                        elif typeAction == 'poly':
                            cmDistance = int(
                                self.multiplierMmPx * distancePoint(drawingPoints[-1], [event.x, event.y]) / 10)
                            self.pointerLine = self.canvas.create_line(drawingPoints[-1][0], drawingPoints[-1][1],
                                                                       event.x, event.y, dash=(3, 5), width=1)
                        distanceLabel.config(text=str(cmDistance))

                    mouseDistance = [int(self.multiplierMmPx * event.x / 10), int(self.multiplierMmPx * event.y / 10)]
                    mouseLabel.config(text=str(mouseDistance))
                except:
                    forceUnlock()

            def actionEvent(line):
                absCoords = []
                actionFlag = empty
                backgroundShape = None
                for coordinates in line:
                    absCoords.append(self.extractCoordinates(coordinates))

                if typeAction == 'cross':
                    actionFlag = crossEventsFlags[crossEvents.index(alarmType.get())]
                elif typeAction == 'rect':
                    actionFlag = rectEventsFlags[rectEvents.index(alarmType.get())]
                elif typeAction == 'oval':
                    actionFlag = ovalEventsFlags[ovalEvents.index(alarmType.get())]
                elif typeAction == 'poly':
                    actionFlag = polyEventsFlags[polyEvents.index(alarmType.get())]
                    if line[-1] == line[0]:
                        corners = line[0:-1]
                    else:
                        corners = line
                    backgroundShape = self.canvas.create_polygon([item for sublist in corners for item in sublist],
                                                                 outline="", fill=ALARMBACKGROUND)

                self.canvasAlarm.append(
                    [typeAction, line, self.canvasItems, absCoords, stabilityTimeVar.get(), actionFlag,
                     alarmColor.get(), backgroundShape])
                forceUnlock()

            def endPolyTerminate(event):
                if len(drawingPoints) > 2:
                    actionEvent(drawingPoints)
                    forceUnlock()
                elif not self.activeAction.locked():
                    forceUnlock()

            def endPolyClose(event):
                try:
                    drawingPoints.append(drawingPoints[0])
                    self.canvasItems.append(self.canvas.create_line(drawingPoints[-2][0], drawingPoints[-2][1],
                                                                    drawingPoints[-1][0], drawingPoints[-1][1],
                                                                    dash=(3, 5),
                                                                    width=1))
                    endPolyTerminate(event)
                except:
                    forceUnlock()

            def forceUnlock(event=None):
                self.canvasItems = []
                if stabilityTimeLabel:
                    stabilityTimeLabel.destroy()
                    stabilityTime.destroy()
                if eventRadio:
                    for i in range(0, len(eventRadio)):
                        eventRadio[i].destroy()
                if colorRadio:
                    for i in range(0, len(colorRadio)):
                        colorRadio[i].destroy()
                actionLabel.config(text='inactive')
                mouseLabel.config(text='inactive')
                distanceLabel.config(text='inactive')
                self.canvas.unbind("<Motion>")
                self.canvas.unbind("<Button-2>")
                self.master.unbind("<s>")
                self.master.unbind("<c>")
                self.master.unbind("<space>")
                if self.pointerLine:
                    self.canvas.delete(self.pointerLine)
                if self.canvasItems:  # should delete partial poly but it does not work
                    for item in self.canvasItems:
                        self.canvas.delete(item)
                if self.activeAction.locked():
                    self.activeAction.release()

            if self.activeAction.acquire(False):
                if platform.system() == 'Linux' or platform.system() == 'Windows':
                    bindIDclick = self.canvas.bind("<Button-3>", defineAction)
                else:
                    bindIDclick = self.canvas.bind("<Button-2>", defineAction)
                bindIDmove = self.canvas.bind("<Motion>", traceAction)
                self.master.bind("<s>", forceUnlock)
                if typeAction == 'poly':
                    # bindClosure = self.master.bind('<c>', endPolyClose)
                    # bindClosureOpen = self.master.bind('<space>', endPolyTerminate)
                    self.master.bind('<c>', endPolyClose)
                    self.master.bind('<space>', endPolyTerminate)

        def deleteAlarm():

            def alarmFound(event):

                # for zone in self.canvasAlarm:
                for i in range(0, len(self.canvasAlarm)):
                    zone = self.canvasAlarm[i]
                    if zone[0] == 'oval':
                        centre = [(zone[1][0][0] + zone[1][1][0]) / 2, (zone[1][0][1] + zone[1][1][1]) / 2]
                        radiusX = (zone[1][0][0] - zone[1][1][0]) / 2
                        radiusY = (zone[1][0][1] - zone[1][1][1]) / 2
                        if pointOnEllipse([event.x, event.y], centre, radiusX, radiusY):
                            distance = 0
                        else:
                            distance = nearbyDistance
                    elif zone[0] == 'rect':
                        distance = distanceFromRect(zone[1], [event.x, event.y])
                    else:
                        distance = distanceFromPoly(zone[1], [event.x, event.y])
                    if distance < nearbyDistance:
                        self.canvas.delete(self.pointerLine)
                        self.canvasItems = [zone[2], i]
                        self.pointerLine = self.canvas.create_oval(event.x - nearbyDistance, event.y - nearbyDistance,
                                                                   event.x + nearbyDistance, event.y + nearbyDistance,
                                                                   fill="red", outline="red", width=1)
                        for item in self.canvasItems[0]:
                            try:
                                self.canvas.itemconfig(item, outline="red")
                            except:
                                self.canvas.itemconfig(item, fill="red")
                        break
                    else:
                        self.canvas.delete(self.pointerLine)
                        if self.canvasItems:
                            for item in self.canvasItems[0]:
                                try:
                                    self.canvas.itemconfig(item, outline="black")
                                except:
                                    self.canvas.itemconfig(item, fill="black")
                        self.canvasItems = []

            def deleteSpecificAlarm(event):
                for item in self.canvasItems[0]:
                    self.canvas.delete(item)
                    del self.canvasAlarm[self.canvasItems[1]]
                closeAction()

            def closeAction(event=None):
                if self.pointerLine:
                    self.canvas.delete(self.pointerLine)
                if self.canvasItems:
                    for item in self.canvasItems[0]:
                        try:
                            self.canvas.itemconfig(item, outline="black")
                        except:
                            self.canvas.itemconfig(item, fill="black")
                self.canvas.unbind("<Motion>", bindIDmove)
                self.canvas.unbind("<Button-2>", bindIDclick)
                self.master.unbind("s>")
                try:
                    actionLabel.config(text='inactive')
                except:
                    pass
                if self.activeAction.locked():
                    self.activeAction.release()

            if self.activeAction.acquire(False):
                if platform.system() == 'Linux' or platform.system() == 'Windows':
                    bindIDclick = self.canvas.bind("<Button-3>", deleteSpecificAlarm)
                else:
                    bindIDclick = self.canvas.bind("<Button-2>", deleteSpecificAlarm)
                bindIDmove = self.canvas.bind("<Motion>", alarmFound)
                self.master.bind("<s>", closeAction)
                actionLabel.config(text='delete')

        # bind escape to terminate
        master.bind('<Escape>', quit)

        # gui canvas defined
        frameButtons.pack(padx=20, pady=20)
        frameEntry.pack(padx=20, pady=20)
        frameRadio.pack(padx=20, pady=20)
        frameColors.pack(padx=20, pady=20)
        frameData.pack(padx=20, pady=20)
        frameData.grid_columnconfigure(1, minsize=100)

        # action butting defined
        Button(frameButtons, text='CROSS', command=defineActionMenuCross).grid(row=0, column=0)
        Button(frameButtons, text='RECT', command=defineActionMenuRect).grid(row=0, column=1)
        Button(frameButtons, text='POLY', command=defineActionMenuPoly).grid(row=0, column=2)
        Button(frameButtons, text='OVAL', command=defineActionMenuOval).grid(row=0, column=3)
        Button(frameButtons, text='DELETE', command=deleteAlarm).grid(row=0, column=4)

        # set data on pointer
        actionLabel = Label(frameData, text="inactive")
        actionLabel.grid(row=0, column=0)
        mouseLabel = Label(frameData, text="inactive")
        mouseLabel.grid(row=0, column=1)
        distanceLabel = Label(frameData, text="inactive")
        distanceLabel.grid(row=0, column=2)

    ## scale the alarm and the temporary mouse pointer

    def scaleAlarmDrawing(self):
        for i in range(0, len(self.canvasAlarm)):
            scaledCoord = []
            for coord in self.canvasAlarm[i][3]:
                scaledCoord.append(self.adjustedCoordinates(coord))
            if self.canvasAlarm[i][0] == 'cross':
                self.canvas.delete(self.canvasAlarm[i][2])
                self.canvasAlarm[i][2] = self.canvas.create_line(scaledCoord[0][0], scaledCoord[0][1],
                                                                 scaledCoord[1][0], scaledCoord[1][1],
                                                                 dash=(3, 5), width=1)
            elif self.canvasAlarm[i][0] == 'rect':
                self.canvas.delete(self.canvasAlarm[i][2])
                self.canvasAlarm[i][2] = self.canvas.create_rectangle(scaledCoord[0][0], scaledCoord[0][1],
                                                                      scaledCoord[1][0], scaledCoord[1][1],
                                                                      dash=(3, 5), width=1, fill=ALARMBACKGROUND)
            elif self.canvasAlarm[i][0] == 'oval':
                self.canvas.delete(self.canvasAlarm[i][2])
                self.canvasAlarm[i][2] = self.canvas.create_oval(scaledCoord[0][0], scaledCoord[0][1],
                                                                 scaledCoord[1][0], scaledCoord[1][1],
                                                                 dash=(3, 5), width=1, fill=ALARMBACKGROUND)
            elif self.canvasAlarm[i][0] == 'poly':
                for item in self.canvasAlarm[i][2]:
                    self.canvas.delete(item)
                self.canvas.delete(self.canvasAlarm[i][7])
                self.canvasAlarm[i][2] = []
                for j in range(1, len(scaledCoord)):
                    self.canvasAlarm[i][2].append(self.canvas.create_line(scaledCoord[j - 1][0], scaledCoord[j - 1][1],
                                                                          scaledCoord[j][0], scaledCoord[j][1],
                                                                          dash=(3, 5), width=1))
                if self.canvasAlarm[i][1][-1] == self.canvasAlarm[i][1][0]:
                    corners = scaledCoord[0:-1]
                else:
                    corners = scaledCoord[1]
                self.canvasAlarm[i][7] = self.canvas.create_polygon([item for sublist in corners for item in sublist],
                                                                    outline="", fill=ALARMBACKGROUND)

    # MONITOR menu

    ## toggles on/off the monitoring
    def monitorWindowToggle(self, forceOff=False):

        if forceOff:
            if self.monitorActive.locked():
                self.monitorActive.release()
            self.monitor['text'] = "MONITOR OFF"
        else:
            if not self.monitorActive.locked():
                if self.demoKit.serverConnected:
                    self.monitorActive.acquire()
                    self.monitor['text'] = "MONITOR ON"
                else:
                    self.monitor['text'] = "MONITOR OFF"
            else:
                self.monitorActive.release()
                self.monitor['text'] = "MONITOR OFF"

    ## execute the monitoring
    # TODO: does not use the stability frame input yet

    def monitorForEvents(self):

        ### Data used in self.canvasAlarm follows this format
        ### [type, canvas coords, ID canvas items, abs coordinates, stability, event flags, color, background]
        ### it tracks each person differently, so the results depends also on the tracking consistency
        try:
            if len(self.canvasAlarm) != len(self.eventStatus):
                ### we create the array of the zone data plus N cumulative flags, one per person
                self.eventStatus = []
                for zoneDef in self.canvasAlarm:
                    statusEntry = [zoneDef]
                    for i in range(0, len(self.positionData)):
                        statusEntry.append(empty)
                    self.eventStatus.append(statusEntry)

            for event in self.eventStatus:
                eventHappened = False
                if event[0][7]:
                    background = event[0][7]
                else:
                    background = event[0][2]
                for i in range(0, len(self.positionData)):
                    # check for new flag, then all flags, then show alarm by changing fill of the item
                    event[i + 1] = self.pointPositionVSshape(self.positionData[i], event[0][3], event[0][0],
                                                             event[i + 1])
                    if event[i + 1] == event[0][5]:
                        self.canvas.itemconfig(background, fill=event[0][6], stipple='gray50')
                        eventHappened = True
                    elif not eventHappened:
                        self.canvas.itemconfig(background, fill=ALARMBACKGROUND)
        except:
            # captures possible corrupted data form the device and skips it
            pass

    ## check what is the positional relationship between the point and the shape
    @staticmethod
    def pointPositionVSshape(point, shape, shapeType, cumulativeFlags):

        pointInside = False
        sideLine = 0

        if point != [0, 0]:
            isPresent = True
            if shapeType == 'oval':
                centre = [(shape[0][0] + shape[1][0]) / 2, (shape[0][1] + shape[1][1]) / 2]
                radiusX = (shape[0][0] - shape[1][0]) / 2 + 2 * nearbyDistance
                radiusY = (shape[0][1] - shape[1][1]) / 2 + 2 * nearbyDistance
                pointInside = pointInEllipse(point, centre, radiusX, radiusY)
            elif shapeType == 'cross':
                sideLine = whichSideIsPoint(point, shape)
            else:
                if shapeType == 'rect':
                    polygon = [shape[0], [shape[1][0], shape[0][1]], shape[1],
                               [shape[0][0], shape[1][1]], shape[0]]
                else:
                    polygon = shape
                pointInside = isPointInPoly(point, polygon)

            if (cumulativeFlags == empty) and not isPresent: return empty
            if (cumulativeFlags == isInside) and (not pointInside) and isPresent: return exiting
            if (cumulativeFlags == isOutside) and pointInside: return entering
            if (cumulativeFlags == isInside) and (not isPresent): return disappearing
            if (cumulativeFlags == isLeft) and (sideLine < 0): return fromLeft
            if (cumulativeFlags == isRight) and (sideLine > 0): return fromRight
            if pointInside: return isInside
            if sideLine > 0: return isLeft
            if sideLine < 0: return isRight
            return isOutside


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
