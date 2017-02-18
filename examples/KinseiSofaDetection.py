#!/usr/bin/python3

"""KinseiSofaDetection.py: example of simple helped sofa detection"""

import sys
import ipaddress
from tkinter import *

sys.path.insert(0, '../libs')
import KinseiClient

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.1.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "in progress"

# the color array is used to simplify color assignment to the tracking balls
colors = ["green", "blue", "red", "magenta", "white", "cyan", "black", "yellow"]
        
# set the tracking canvas dimensions
screenX = 600
screenY = 600
        
# this class shows how to visualise tracking with tkinter
class ViewerStableTracking:
    def __init__(self, ip):
        self.sofaCorners = []
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
        except:
            self.connected = False
            
    def personOfInterest(self, index):
        if self.isConnected():
            self.index = index
            
    def isConnected(self):
        return self.connected
    
    def maxNumberPersons(self):
        return len(self.demoKit.getPersonsPositions(False))
    
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
            self.master.title("Kinsei Find the Sofa Demo")
            
            # bind escape to terminate
            self.master.bind('<Escape>', quit)
            
            self.canvas = Canvas(self.master, width=(screenX + 10), height=(screenY + 10))
            self.canvas.pack()
            self.canvas.create_rectangle(10, 10, screenX, screenY, dash=(5,5), outline="blue")
            titleId1 = self.canvas.create_text(screenX / 2 - 70, screenY - 20, anchor="nw", font=('Helvetica', 14))
            self.canvas.itemconfig(titleId1, text="Tracking person " + str(self.index))
            positionData = self.demoKit.getPersonsPositions(False)
            
            self.person = [self.canvas.create_oval(0, 0, 20, 20, fill="red"),[0,0]]
                
            # the following method starts the tracking
            self.trackPersons()
            self.master.mainloop()
            
    # executes the tracking
    def trackPersons(self):
        positionData = self.demoKit.getStablePosition(self.index,500,2);
        if (positionData != False):  
            self.sofaCorners.append([self.canvas.create_oval(0, 0, 20, 20, fill="green"),positionData])
            currentPositionData = self.adjustedCoordinates(positionData);
            deltax = currentPositionData[0] - self.person[1][0]
            deltay = currentPositionData[1] - self.person[1][1]
            self.canvas.move(self.person[0], deltax, deltay)
            self.canvas.move(self.sofaCorners[-1], deltax, deltay)
            self.person[1] = currentPositionData
            
        self.canvas.after(10, self.trackPersons) # delay must be larger than 0
    
# this class is used to get the IP of the device from the user
class StartGUI:
    def __init__(self, master):
        self.device = None
        self.master = master
        master.title("Kinsei Viewer Demo")
        
        Label(master, text='Insert the device IP').pack(side=TOP,padx=130,pady=5)
        self.ipEntry = Entry(master, width=20, justify='center')
        self.ipEntry.pack(side=TOP,padx=10,pady=5)
        self.ipEntry.insert(0,"192.168.1.42")
        
        Label(master, text='Index of person to track ').pack(side=TOP,padx=130,pady=5)
        self.personEntry = Entry(master, width=5,  justify='center')
        self.personEntry.pack(side=TOP,padx=10,pady=10)
        self.personEntry.insert(0,"0")
        
        # bind escape to terminate
        master.bind('<Escape>', quit)
        
        Button(master, text='Connect', command=self.connectDevice).pack(side=LEFT,padx=10, pady=5)
        Button(master, text='Quit', command=master.quit).pack(side=RIGHT, padx=10, pady=5)


    def connectDevice(self):
        # the module ipaddress is used to verify the validity of the entered IP address
        if (self.device == None):
            try:
                ipaddress.ip_address(self.ipEntry.get())
            except:
                self.ipEntry.configure(fg="red")
                return
            
            self.ipEntry.configure(fg="black")
            self.device = ViewerStableTracking(self.ipEntry.get())
        
        if self.device.isConnected():
            if (int(self.personEntry.get()) < self.device.maxNumberPersons()):
                self.device.personOfInterest(int(self.personEntry.get()))
                self.master.destroy()
                self.device.start()
            else:
                self.personEntry.configure(fg="red")
                self.ipEntry.configure(state='readonly')
        else:
            self.ipEntry.configure(fg="red")
        
def start():        
    root = Tk()
    kinseiStart = StartGUI(root)
    root.mainloop()
    
    
if __name__ == "__main__": start()
    
    