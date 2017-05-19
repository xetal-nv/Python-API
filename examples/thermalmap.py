#!/usr/bin/python3

"""thermalmap.py: basic graphical viewer for the thermal map"""

import sys
import ipaddress
from tkinter import *
from math import *

sys.path.insert(0, '../libs')
import KinseiClient

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.5.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "in development"

# the color array is used to simplify color assignment to the tracking balls
colors = ["green", "blue", "magenta", "white", "cyan", "black", "yellow", "red"]
        
# set the screen maximum dimensions
maxScreenX = 1000
maxScreenY = 800
offset = 10

        
# this class shows how to visualise tracking with tkinter
class ThermalMap:

    def __init__(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
        except:
            self.connected = False
            
    def isConnected(self):
        return self.connected
    
    # the KinseiClient class provides coordinates in mm and absolute
    # here we scalte to cm and made them relative to our canvas
    def adjustedCoordinates(self, coordinates):
        coordX = int((coordinates[0] / 10) * ((self.screenX * 10) / self.roomSize[0])) +  offset
        coordY = int((coordinates[1] / 10) * ((self.screenY * 10) / self.roomSize[1])) +  offset
        return [coordX, coordY]
    
    def defineCanvas(self):
        boundingBoxRatio = self.roomSize[0] / self.roomSize[1]
        screenRatio = maxScreenX / maxScreenY
        if (screenRatio < 1):
            # portrait screen
            if ((boundingBoxRatio < 1) and (screenRatio > boundingBoxRatio)):
                #We need to scale from the height
                yMax = maxScreenY
                yMin = 0
                theOtherDimension = trunc((yMax - yMin) * boundingBoxRatio)
                xMin = trunc((maxScreenX - theOtherDimension) /2)
                xMax = xMin + theOtherDimension
            else:
                #We need to scale from the width
                xMin = 0
                xMax = maxScreenX
                theOtherDimension = trunc((xMax - xMin) / boundingBoxRatio)
                yMin = 0
                yMax = yMin + theOtherDimension
        else:
            # landscape screen
            if ((boundingBoxRatio > 1) and (screenRatio < boundingBoxRatio)):
                # We need to scale from the width
                xMin = 0
                xMax = maxScreenX
                theOtherDimension = trunc((xMax - xMin) / boundingBoxRatio);
                yMin = 0;
                yMax = yMin + theOtherDimension;

            else:
                # We need to scale from the height
                yMax = maxScreenY
                yMin = 0
                theOtherDimension = trunc((yMax - yMin) * boundingBoxRatio)
                xMin = trunc((maxScreenX - theOtherDimension) /2)
                xMax = xMin + theOtherDimension
        self.screenX = xMax - xMin
        self.screenY = yMax - yMin
    
    # this function set-up the canvas and let the tracking start
    def start(self):
        if self.connected:
            # the canvas is created and all elements initialisated
            self.roomSize = self.demoKit.getRoomSize()
            self.defineCanvas()
            self.master = Tk()
            self.master.title("Kinsei Thermal Map Demo")
            
            # bind escape to terminate
            self.master.bind('<Escape>', quit)
            
            self.canvas = Canvas(self.master, width=(self.screenX + 2*offset), height=(self.screenY + 2*offset))
            self.canvas.pack()
            self.canvas.create_rectangle(10, 10, self.screenX + offset, self.screenY + offset, dash=(5,5), outline="red")
            realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
            self.canvas.create_polygon(*realVertex,fill='', outline = 'blue')
            print (realVertex)
            positionData = self.demoKit.getPersonsPositions(False);
            
#             self.persons =[]
#             for i in range(0, len(positionData)):
#                 person = self.canvas.create_oval(0, 0, 20, 20, fill=colors[i % len(colors)])
#                 self.persons.append([person,[0,0]])
                
            # the following method starts the fusion map
            self.drawMap()
            self.master.mainloop()
            
    # executes the tracking
    def drawMap(self):
#         positionData = self.demoKit.getPersonsPositions();
#         
#         for i in range(0, len(positionData)):
#             currentPositionData = self.adjustedCoordinates(positionData[i]);
#             deltax = currentPositionData[0] - self.persons[i][1][0]
#             deltay = currentPositionData[1] - self.persons[i][1][1]
#             self.canvas.move(self.persons[i][0], deltax, deltay)
#             self.persons[i][1] = currentPositionData
            
        self.canvas.after(10, self.drawMap) # delay must be larger than 0
    
# this class is used to get the IP of the device from the user
class StartGUI:
    def __init__(self, master):
        self.master = master
        master.title("Kinsei Viewer Demo")
        Label(master, text='Insert the device IP').pack(side=TOP,padx=130,pady=10)
        
        self.ipEntry = Entry(master, width=20)
        self.ipEntry.pack(side=TOP,padx=10,pady=10)
        self.ipEntry.insert(0,"192.168.42.1")
        
        # bind escape to terminate
        master.bind('<Escape>', quit)
        
        Button(master, text='Connect IP', command=self.connectDeviceIP).pack(side=LEFT,padx=10, pady=5)
        Button(master, text='Connect DNS', command=self.connectDeviceDNS).pack(side=LEFT,padx=10, pady=5)
        Button(master, text='Quit', command=master.quit).pack(side=RIGHT, padx=10, pady=5)


    def connectDeviceIP(self):
        # the module ipaddress is used to verify the validity of the entered IP address
        try:
            ipaddress.ip_address(self.ipEntry.get())
        except:
            self.ipEntry.configure(fg="red")
            return
        
        self.ipEntry.configure(fg="black")
        self.device = ThermalMap(self.ipEntry.get())
        
        if self.device.isConnected():
            self.master.destroy()
            self.device.start()
        else:
            self.ipEntry.configure(fg="red")
            
    def connectDeviceDNS(self):
        # the module ipaddress is used to verify the validity of the entered IP address
        
        self.ipEntry.configure(fg="black")
        self.device = ThermalMap(self.ipEntry.get())
        
        if self.device.isConnected():
            self.master.destroy()
            self.device.start()
        else:
            self.ipEntry.configure(fg="red")
        
def start():        
    root = Tk()
    kinseiStart = StartGUI(root)
    root.mainloop()
    
    
if __name__ == "__main__": start()
