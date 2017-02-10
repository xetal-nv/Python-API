#!/usr/bin/python3

"""trackingViewer.py: basic graphical viewer for persons tracking only"""

import sys
import ipaddress
from tkinter import *

from random import randint

sys.path.insert(0, '../libs')
import KinseiClient

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "in progress"

colors = ["green", "blue", "red", "magenta", "white", "cyan", "black", "yellow"]

class Person:
    def __init__(self, canvas, x1, y1, x2, y2, color="green"):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.canvas = canvas
        self.person = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill=color)

    def track_person(self):
        deltax = randint(0,5)
        deltay = randint(0,5)
        self.canvas.move(self.person, deltax, deltay)
        self.canvas.after(50, self.track_person)
        
class ViewerTrackingOnly:
    def __init__(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
        except:
            self.connected = False
            
    def isConnected(self):
        return self.connected
    
    def adjustedCoordinates(self, coordinates):
        coordX = int((coordinates[0] / 10) * (8000 / self.roomSize[0]))
        coordY = int((coordinates[1] / 10) * (8000 / self.roomSize[1]))
        return [coordX, coordY]
    
    def start(self):
        if self.connected:
            self.roomSize = self.demoKit.getRoomSize()
            self.master = Tk()
            self.master.title("Kinsei Viewer Demo")
            self.canvas = Canvas(self.master, width=810, height=810)
            self.canvas.pack()
            self.canvas.create_rectangle(10, 10, 800, 800, dash=(5,5), outline="blue")
            positionData = self.demoKit.getPersonsPositions(False);
            self.persons =[]
            for i in range(0, len(positionData)):
                person = self.canvas.create_oval(0, 0, 20, 20, fill=colors[i])
                self.persons.append([person,[0,0]])
            self.trackPersons()
            self.master.mainloop()
            
    def trackPersons(self):
        positionData = self.demoKit.getPersonsPositions();
        for i in range(0, len(positionData)):
            currentPositionData = self.adjustedCoordinates(positionData[i]);
            deltax = currentPositionData[0] - self.persons[i][1][0]
            deltay = currentPositionData[1] - self.persons[i][1][1]
            self.canvas.move(self.persons[i][0], deltax, deltay)
            self.persons[i][1] = currentPositionData
        self.canvas.after(0, self.trackPersons)
    
class StartGUI:
    def __init__(self, master):
        self.master = master
        master.title("Kinsei Viewer Demo")
        Label(master, text='Insert the device IP').pack(side=TOP,padx=130,pady=10)
        
        self.ipEntry = Entry(master, width=20)
        self.ipEntry.pack(side=TOP,padx=10,pady=10)
        self.ipEntry.insert(0,"192.168.1.42")
        
        Button(master, text='Connect', command=self.connectDevice).pack(side=LEFT,padx=10, pady=5)
        Button(master, text='Quit', command=master.quit).pack(side=RIGHT, padx=10, pady=5)


    def connectDevice(self):
        # the module ipaddress is used to verify the validity of the entered IP address
        try:
            ipaddress.ip_address(self.ipEntry.get())
        except:
            print("invalid IP")
            self.ipEntry.configure(fg="red")
            return
        self.ipEntry.configure(fg="black")
        self.device = ViewerTrackingOnly(self.ipEntry.get())
        if self.device.isConnected():
            self.master.destroy()
            self.device.start()
        else:
            self.ipEntry.configure(fg="red")
                
root = Tk()
kinseiStart = StartGUI(root)
root.mainloop()
    
    
#if __name__ == "__main__": start()
