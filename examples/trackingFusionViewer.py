#!/usr/bin/python3

"""trackingFusionViewer.py: graphical viewer for persons tracking and fusion"""

import sys
import ipaddress
import math
from tkinter import *

sys.path.insert(0, '../libs')
import KinseiClient

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.8"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"

# the color array is used to simplify color assignment to the tracking balls
colors = ["green", "blue", "red", "magenta", "white", "cyan", "black", "yellow"]
        
# set the tracking canvas dimensions
screenX = 600
screenY = 600

# the following methids are used o properly shade a given color
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
        
# this class shows how to visualise tracking with tkinter
class TrackingFusionViewer:
    def __init__(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
            self.fusionMap = []
        except:
            self.connected = False
            
    def isConnected(self):
        return self.connected
    
    # the KinseiClient class provides coordinates in mm and absolute
    # here we scalte to cm and made them relative to our 800x800 canvas
    def adjustedCoordinates(self, coordinates):
        coordX = int((coordinates[0] / 10) * ((screenX * 10) / self.roomSize[0]))
        coordY = int((coordinates[1] / 10) * ((screenY * 10) / self.roomSize[1]))
        return [coordX, coordY]
    
    # this function set-up the canvas and let the tracking start
    def start(self):
        if self.connected:
            # the canvas is created and all elements initialisated
            self.roomSize = self.demoKit.getRoomSize()
            self.master = Tk()
            self.master.title("Kinsei Viewer Demo")
            
            # bind escape to terminate
            self.master.bind('<Escape>', quit)
            
            self.canvas = Canvas(self.master, width=(2 * screenX + 20), height=(screenY + 50))
            self.canvas.pack()
            self.canvas.create_rectangle(10, 10, screenX, screenY, dash=(5,5), outline="blue")
            self.canvas.create_rectangle(screenX + 20, 10, 2*screenX + 10, screenY, dash=(5,5), outline="red")
            
            titleId1 = self.canvas.create_text(screenX / 2 - 70, screenY + 20, anchor="nw", font=('Helvetica', 20))
            self.canvas.itemconfig(titleId1, text="Tracking Canvas")
            titleId2 = self.canvas.create_text(screenX * 1.5 - 50, screenY + 20, anchor="nw", font=('Helvetica', 20))
            self.canvas.itemconfig(titleId2, text="Fusion Canvas")
            
            positionData = self.demoKit.getPersonsPositions(False);
            
            self.persons =[]
            for i in range(0, len(positionData)):
                person = self.canvas.create_oval(0, 0, 20, 20, fill=colors[i % len(colors)])
                self.persons.append([person,[0,0]])
                
            # the following method starts the tracking
            self.trackPersonsAndFusion()
            self.master.mainloop()
            
    # executes the tracking
    def trackPersonsAndFusion(self):
        positionData = self.demoKit.getPersonsPositions();
        fusionData = self.demoKit.getFusionValues(False);
        
        self.updateFusionMap(fusionData)
        
        for i in range(0, len(positionData)):
            currentPositionData = self.adjustedCoordinates(positionData[i]);
            deltax = currentPositionData[0] - self.persons[i][1][0]
            deltay = currentPositionData[1] - self.persons[i][1][1]
            self.canvas.move(self.persons[i][0], deltax, deltay)
            self.persons[i][1] = currentPositionData
            
        self.canvas.after(10, self.trackPersonsAndFusion) # delay must be larger than 0
        
    # draw the fusion map
    def updateFusionMap(self, fusionData):
        # clean the current fusion map
        for i in range(0, len(self.fusionMap)):
            self.canvas.delete(self.fusionMap[i])
        self.fusionMap = []
        for i in range(0, len(fusionData)):
            currentPositionData = self.adjustedCoordinates([fusionData[i][0],fusionData[i][1]]);
            x0 = currentPositionData[0] + screenX + 10
            y0 = currentPositionData[1]
            x1 = currentPositionData[0] + screenX + 30
            y1 = currentPositionData[1] + 20
            self.fusionMap.append(self.canvas.create_oval(x0,y0,x1,y1, fill=colorscale("#adff2f",fusionData[i][2]/26)))
            
    
# this class is used to get the IP of the device from the user
class StartGUI:
    def __init__(self, master):
        self.master = master
        master.title("Kinsei Viewer Demo")
        Label(master, text='Insert the device IP').pack(side=TOP,padx=130,pady=10)
        
        self.ipEntry = Entry(master, width=20)
        self.ipEntry.pack(side=TOP,padx=10,pady=10)
        self.ipEntry.insert(0,"192.168.1.42")
        
        # bind escape to terminate
        master.bind('<Escape>', quit)
        
        Button(master, text='Connect', command=self.connectDevice).pack(side=LEFT,padx=10, pady=5)
        Button(master, text='Quit', command=master.quit).pack(side=RIGHT, padx=10, pady=5)


    def connectDevice(self):
        # the module ipaddress is used to verify the validity of the entered IP address
        try:
            ipaddress.ip_address(self.ipEntry.get())
        except:
            self.ipEntry.configure(fg="red")
            return
        
        self.ipEntry.configure(fg="black")
        self.device = TrackingFusionViewer(self.ipEntry.get())
        
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
