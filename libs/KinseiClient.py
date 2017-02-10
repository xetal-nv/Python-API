#!/usr/bin/python3

"""KinseiClient.py: core client for connecting to a kinsei system"""

import socket
import time

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.9"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "pre-release"

# the class implmeneting the kinser client
class KinseiSocket(object):
    
    kinseiCommand = { 
                 "roomSize":                b'\x73', 
                 "zones":                   b'\x78',
                 "numberPersonsFloat":      b'\x6E',
                 "numberPersonsFixed":      b'\x6D',
                 "personsPosition":         b'\x64',
                 "checkOnline":             b'\x74',
                 "checkSensorsOnline":      b'\x7A',
                 "batteryLevels":           b'\x76',
                 "fusionValues":            b'\x66',
                 "error":                   b'\x65'
                 }
    
    """ 
    The costructor create the socket for a device at the provided IP and port.
    
    Arguments are as follows:
    host: device IP with default value valid for a device in Access Point mode
    timeout: timeout of the connection in ms
    pauseMS: interval forced between commands to the device in ms
    port: device port, 2005 is the default port if not manually changed in the device itself
    """
    def __init__(self,host = '192.168.42.1', timeout = 15.0, pauseMS = 150, port = 2005):
        self.latencyMS = pauseMS
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.settimeout(timeout)
            self.server.connect((host, port))
            self.serverConnected = True
        except socket.error as err:
            self.serverConnected = False
            
    def __del__(self):
        if (self.serverConnected):
            self.server.close()
        
    # set the forced waiting after a socket comunication 
    """
    Set the time interval between to messages forced when the methods below are executes with the flag wait
    set to True
    It is adviced to keep this value not below 150 ms.
    """
    def setTimeIntervalMS(self,pauseMS):
        self.latencyMS = pauseMS
        
    """
    Returns True is the device at the provided IP has been found and connection was possible.
    False otherwise
    """
    def checkIfOnline(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["checkOnline"], wait)
        if (data == self.kinseiCommand["error"]):
            return False
        if (data[1] == 1):
            return True
        return False
    
    """
    Returns the dimension of the bounding box of the room in mm.
    False in case of comunication error
    """
    def getRoomSize(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["roomSize"], wait)
        if (data == self.kinseiCommand["error"]):
            return False
        x = [data[1], data[2]]
        y = [data[3], data[4]]
        return [self.bytes_to_int(x), self.bytes_to_int(y)]
    
    """ 
    Returns an array of dimensions equal to the number of maximum persons being tracked plus one.
    Each element in the array provide the X and Y coordinates of the position or [0,0] in case in invalid values
    
    Please note that the system provides consistent coordinates, meaning that the first coordinates will 
    belog always to the same person until the moment it leaves the monitored space or it overlaps perfectly with another
    person
    
    False is returned in case or connection error
    """
    def getPersonsPositions(self, wait = True):
        # returns [number of persons, [map ID, x,y]]
        data = self.executeCommand(self.kinseiCommand["personsPosition"], wait)
        if (data == self.kinseiCommand["error"]):
            return False
        allPositions =[]
        for i in range(data[1]):
            currentPosition = []
            x = [data[4+6*i], data[5+6*i]]
            y = [data[6+6*i], data[7+6*i]]
            currentPosition.append(self.bytes_to_int(x))
            currentPosition.append(self.bytes_to_int(y))
            allPositions.append(currentPosition)
        return allPositions
    
    """
    Return the number of detected people as a fixed number.
    
    False is returned in case or connection error
    """
    def getNumberPersonsFixed(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["numberPersonsFixed"], wait)
        if (data == self.kinseiCommand["error"]):
            return False
        return data[1]
    
    """
    Retunes the detecte number of people as a decimal number
    
    This method is to be preferred to getNumberPersonsFixed as it allows to set thresholds for proper 
    tuning in determining the actualy number of detected persons.
    
    False is returned in case or connection error
    """
    def getNumberPersonsFloat(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["numberPersonsFloat"], wait)
        if (data == self.kinseiCommand["error"]):
            return False
        return data[1] / 10  
    
    """
    Returns an array with the battery voltage levels of the connected sensors.
    If the sensors are connected to a fix supply, the array will report 0 for each sensor
    
    False is returned in case or connection error
    """
    def getBatteryLevels(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["batteryLevels"], wait)
        if (data == self.kinseiCommand["error"]):
            return False    
        numberSensors = data[1];
        batteryLevels = []    
        for x in range(numberSensors):
            singleBattery = [data[2+2*x], data[3+2*x]]
            batteryLevels.append(self.bytes_to_int(singleBattery) / 100)
        return batteryLevels

    """
    Returns an array indicating which sensor is online and which not
    
    False is returned in case or connection error
    """
    def checkIfSensorsOnline(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["checkSensorsOnline"], wait)
        if (data == self.kinseiCommand["error"]):
            return False    
        numberSensors = data[1];
        sensorsStatus = []    
        for x in range(numberSensors):
            sensorsStatus.append(data[2+5*x])
        return sensorsStatus
    
    """
    Returns an array where each element is an array providing the X and Y coordinates of a possible person detection 
    and a value indicating the confidence level that thay is a real person or not.
    
    False is returned in case or connection error
    """
    def getFusionValues(self, wait = True):
        # returns [[centroid X, centroid Y, sensed value]]
        data = self.executeCommand(self.kinseiCommand["fusionValues"], wait)
        if (data == self.kinseiCommand["error"]):
            return False
        numberSensedLocations = data[1];
        sensedLocationsData = []    
        for i in range(numberSensedLocations):
            locationStatus = []
            x = [data[4+7*i],  data[5+7*i]]
            locationStatus.append(self.bytes_to_int(x))
            y = [data[6+7*i],  data[7+7*i]]
            locationStatus.append(self.bytes_to_int(y))
            locationStatus.append(data[7+7*i] / 10)
            sensedLocationsData.append(locationStatus)
        return sensedLocationsData 
    
    """
    Returns an array with all defines zones of interest.
    Each array will provide a label indicating if the zone is "circular" or "polygonal".
    In case of circular, the X and Y coordinates and the radius will be provides
    In case of polygonal, the X and Y coordinates (in sequence) of each corner will be provided
    
    False is returned in case or connection error
    """
    def getZones(self, wait = True):
        data = self.executeCommand(self.kinseiCommand["zones"], wait)
        if (data == self.kinseiCommand["error"]):
            return False 
        numberZones = data[1];
        zonesSpecs = []
        indexData = 0;
        for x in range(numberZones):
            currentZone = []
            if (data[2 + indexData] == 0):
                currentZone.append("circular")
                centreX = [data[3 + indexData],  data[4 + indexData]]
                centreY = [data[5 + indexData],  data[6 + indexData]]
                radius = [data[7 + indexData],  data[8 + indexData]]
                currentZone.append(self.bytes_to_int(centreX))
                currentZone.append(self.bytes_to_int(centreY))
                currentZone.append(self.bytes_to_int(radius))
                indexData += 7
            else:
                currentZone.append("polygonal")
                numberCorners = data[3 + indexData]
                for y in range(numberCorners):
                    cornerX = [data[4 + indexData + 4*y],  data[5 + indexData + 4*y]]
                    cornerY = [data[6 + indexData + 4*y],  data[7 + indexData + 4*y]]
                    currentZone.append(self.bytes_to_int(cornerX))
                    currentZone.append(self.bytes_to_int(cornerY))
                indexData += (4 * numberCorners + 1)
            zonesSpecs.append(currentZone)
        return zonesSpecs   
    
    """
    Executes any comand and return the message from the devoce at it was received
    
    False is returned in case or connection error
    """
    def executeCommand(self, command, wait = True):
        if (self.serverConnected):
            try:
                self.server.sendall(command)
                data = self.server.recv(1024)
                if (wait): 
                    time.sleep(self.latencyMS / 1000)
                return data
            except socket.error as err:
                return self.kinseiCommand["error"]
        else:
            return self.kinseiCommand["error"] 

    """
    Internal methods
    """ 
    def bytes_to_int(self, bytes):
        result = 0
        for b in bytes:
            result = result * 256 + int(b)
        return result
    