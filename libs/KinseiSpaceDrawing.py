#!/usr/bin/python3

"""KinseiSpaceDrawing.py: set of functions allowing manupulation of positional data"""

from tkinter import *
import math
import KinseiClient


__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.1.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"

# the class implmeneting the kinser client
class KinseiCanvas(object):
    
    """ __init__:    
    Constructor checking the connection and setting internal variables.
    Arguments are as follows:
    deviceSocket:         a KinseiSocket object connected to the device to be used
    """
    def __init__(self, deviceSocket):
        try:
            if (deviceSocket.checkIfOnline(False)):
                self.device = deviceSocket
            else:
                self.device = None
        except socket.error as err:
            self.device = None
            
    """ isConnected:    
    Return True is the object is connected, False otherwise
    """
    def isConnected(self):
        if self.device is None:
            return False
        return True
    
    """ viewCanvas:    
    IN PROGRESS
    """
    def viewCanvas(self, screenX, screenY):
        if self.isConnected():
            # the canvas is created and all elements initialisated
            self.roomSize = self.device.getRoomSize()
            if self.roomSize == False:
                return False
            self.master = Tk()
            self.master.title("Kinsei Canas Viewer")
            
            # bind escape to terminate
            self.master.bind('<Escape>', quit)
            
            self.canvas = Canvas(self.master, width=(screenX + 10), height=(screenY + 10))
            self.canvas.pack()
            self.canvas.create_rectangle(10, 10, screenX, screenY, dash=(5,5), outline="blue")
            
            self.master.mainloop()
            return True
        else:
            return False
        
    """ getStablePosition:    
    Returns a position, if possible, that is stable for a given ammount of time
    Arguments are as follows:
    whichPerson:         which person to be checked
    timeMS:              time interval for stability 
    howManyTries:        maximum number of tries
    """
    def getStablePosition(self, whichPerson = 0, timeMS = 2000, howManyTries = 5):
        iterations = math.floor(timeMS / self.device.getTimeIntervalMS())
        for i in range(0,howManyTries):
            newPosition = self.device.getPersonsPositions()[whichPerson]
            stable = True
            for ii in range(0,iterations):
                currentPosition = self.device.getPersonsPositions()[whichPerson]
                if (currentPosition != newPosition):
                    stable = False
                    break
            if stable:
                return newPosition
        return False


def test():
    IP_DEVICE = '81.82.231.115' # in AP mode it is '192.168.1.42' otherwise check your network
    demoKit = KinseiClient.KinseiSocket(IP_DEVICE)
    demoKitCanvas = KinseiCanvas(demoKit)
    
    
if __name__ == "__main__": test()
    
    