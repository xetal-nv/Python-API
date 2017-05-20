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
__version__     =   "1.0.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"

        
# set the viewing window
maxScreenX = 1000 # maximum X size of screen window in pixels
maxScreenY = 800 # maximum Y size of screen window in pixels
offset = 10 # padding offset in pixels

# types of thermal maos
thermalType = ["linear", "personTracking"]

# Temperature range in Celsius (if supported by the thermal map mode)
minimimTemp = 15
maximumTemp = 80
        
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
    
    def colorEquivalent(self,temp10):
        # these values could be changed or made parameters for generalisation
        minval, maxval = 0, 4
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # [BLUE, GREEN, RED]
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

#         if (temp10 > 250):
#             return "#FF0000"
#         else:
#             return ""
    
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
            
            # set the common variable background values
            self.canvas = Canvas(self.master, width=(self.screenX + 2*offset), height=(self.screenY + 2*offset))
            self.canvas.pack()
            self.realVertex = list(map(self.adjustedCoordinates, self.demoKit.getRoomCorners()))
            self.thermalMapSettings = self.demoKit.getThermalMapResolution()
            self.grid = self.canvas.grid(row=0,column=0)
            self.drawBackground()
                        
            self.drawMap()
            self.master.mainloop()
            
            
    # draw background
    def drawBackground(self):
            self.canvas.create_rectangle(10, 10, self.screenX + offset, self.screenY + offset, dash=(5,5), outline="red", width='3')
            self.canvas.create_polygon(*self.realVertex,fill='', outline = 'blue', width='3')
        
    # executes the thermal map
    # currently random colors
    def drawMap(self):
        self.canvas.delete("all")
        w=self.screenX
        h=self.screenY
        colors = list(map(self.colorEquivalent,self.demoKit.getThermalMapPixels()))
                
        # draws the map
        cellwidth = w/self.thermalMapSettings[0]
        cellheight=h/self.thermalMapSettings[1]
        for row in range(self.thermalMapSettings[1]):
            for col in range(self.thermalMapSettings[0]):
                self.canvas.create_rectangle(col*cellwidth + offset,row*cellheight + offset,
                                             (col+1)*cellwidth + offset,(row+1)*cellheight + offset, 
                                             fill= colors[row*self.thermalMapSettings[0] + col],outline="")
                    
        self.drawBackground()
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
