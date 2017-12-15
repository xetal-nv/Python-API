#!/usr/bin/python3

"""KinseiClient.py: core client for connecting to a kinsei system"""

import socket
import time
import math

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "2.3.7"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredtrackingserver__ = "february2017 or later"


# the class implementing the kinsei client
class KinseiSocket(object):
    kinseiCommand = {
        "roomSize": b'\x73',
        "zones": b'\x78',
        "numberPersonsFloat": b'\x6E',
        "numberPersonsFixed": b'\x6D',
        "personsPosition": b'\x64',
        "checkOnline": b'\x74',
        "checkSensorsOnline": b'\x7A',
        "batteryLevels": b'\x76',
        "fusionValues": b'\x66',
        "thermres": b'\x1A',
        "thermmap": b'\x1B',
        "error": b'\x65'
    }

    """ __init__:
    The costructor create the socket for a device at the provided IP and port.
    
    Arguments are as follows:
    host:             device IP with default value valid for a device in Access Point mode
    timeout:          timeout of the connection in ms
    pauseMS:          interval forced between commands to the device in ms (>55ms)
    port:             device port, 2005 is the default port if not manually changed in the device itself
    """

    def __init__(self, host='192.168.76.1', timeout=15.0, pauseMS=55, port=2005):
        self.latencyMS = pauseMS
        self.stablePositions = []
        self.stablePositionsFrames = []
        self.radiusStability = 200
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.channelData = [(host, port), timeout]
            self.server.settimeout(timeout)
            self.server.connect((host, port))
            self.serverConnected = True
        except socket.error as err:
            self.serverConnected = False

    """ __del__:
    Destructor
    """

    def __del__(self):
        self.disconnect()

    """ disconnect:
    Disconnect from the device without removing the object"""

    def disconnect(self):
        if self.serverConnected:
            self.serverConnected = False
            self.server.close()
        return self.serverConnected

    """reconnect:
    Reconnect to the channel associated with the object"""

    def reconnect(self):
        if not self.serverConnected:
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.settimeout(self.channelData[1])
                self.server.connect(self.channelData[0])
                self.serverConnected = True
            except socket.error as err:
                self.serverConnected = False
            finally:
                return self.serverConnected

    """ setTimeIntervalMS:
    Set the time interval between two messages, forced when the methods below are executes with the flag wait
    set to True
    It is adviced to keep this value above 50 ms.
    """

    def setTimeIntervalMS(self, pauseMS):
        self.latencyMS = pauseMS

    """ getTimeIntervalMS:
    Returns the time interval between to messages forced when the methods below are executes with the flag wait
    set to True
    """

    def getTimeIntervalMS(self):
        return self.latencyMS


    """ setTimeIntervalMS:
    Set the space radius in mm for a position to be considered stable
    It is adviced to keep this value above 5 mm.
    """

    def setStabilityRadius(self, radiusMM):
        self.radiusStability = radiusMM

    """ getTimeIntervalMS:
    Returns the space radius in mm for a position to be considered stable
    set to True
    """

    def getStabilityRadius(self):
        return self.radiusStability

    """ checkIfOnline:
    Returns True is the device at the provided IP has been found and connection was possible.
    False otherwise
    """

    def checkIfOnline(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["checkOnline"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        if data[1] == 1:
            return True
        return False

    """ getRoomSize:
    Returns the dimension of the bounding box of the room in mm.
    False in case of comunication error
    """

    def getRoomSize(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["roomSize"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        x = [data[1], data[2]]
        y = [data[3], data[4]]
        return [self.bytes_to_int(x), self.bytes_to_int(y)]

    """ getRoomCorners:
    Returns the position of the corners of the room in mm.
    False in case of comunication error
    """

    def getRoomCorners(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["roomSize"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        cornersNumber = data[5]
        roomCorners = []
        for i in range(0, cornersNumber):
            currentCorner = []
            x = [data[6 + 4 * i], data[7 + 4 * i]]
            y = [data[8 + 4 * i], data[9 + 4 * i]]
            currentCorner.append(self.bytes_to_int(x))
            currentCorner.append(self.bytes_to_int(y))
            roomCorners.append(currentCorner)
        return roomCorners

    """ getPersonsPositions:
    Returns an array of dimensions equal to the number of maximum persons being tracked plus one.
    Each element in the array provide the X and Y coordinates of the position or [0,0] in case in invalid values
    
    Please note that the system provides consistent coordinates, meaning that the first coordinates will 
    belog always to the same person until the moment it leaves the monitored space or it overlaps perfectly with another
    person
    
    False is returned in case of connection error
    """

    def getPersonsPositions(self, wait=True):
        # returns [number of persons, [map ID, x,y]]
        data = self.executeCommand(self.kinseiCommand["personsPosition"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        allPositions = []
        try:
            for i in range(data[1]):
                currentPosition = []
                x = [data[4 + 6 * i], data[5 + 6 * i]]
                y = [data[6 + 6 * i], data[7 + 6 * i]]
                currentPosition.append(self.bytes_to_int(x))
                currentPosition.append(self.bytes_to_int(y))
                allPositions.append(currentPosition)
        except:
            allPositions = []
        return allPositions

    """ getNumberPersonsFixed:
    Return the number of detected people as a fixed number.
    
    False is returned in case of connection error
    """

    def getNumberPersonsFixed(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["numberPersonsFixed"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        return data[1]

    """ getNumberPersonsFloat:
    Retunes the detected number of people as a decimal number
    
    This method is to be preferred to getNumberPersonsFixed as it allows to set thresholds for proper 
    tuning in determining the actualy number of detected persons.
    
    False is returned in case of connection error
    """

    def getNumberPersonsFloat(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["numberPersonsFloat"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        return data[1] / 10

    """ getBatteryLevels:
    Returns an array with the battery voltage levels of the connected sensors.
    If the sensors are connected to a fix supply, the array will report 0 for each sensor
    
    False is returned in case of connection error
    """

    def getBatteryLevels(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["batteryLevels"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        numberSensors = data[1]
        batteryLevels = []
        for x in range(numberSensors):
            singleBattery = [data[2 + 2 * x], data[3 + 2 * x]]
            batteryLevels.append(self.bytes_to_int(singleBattery) / 100)
        return batteryLevels

    """ checkIfSensorsOnline:
    Returns an array indicating which sensor is online and which not
    
    False is returned in case of connection error
    """

    def checkIfSensorsOnline(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["checkSensorsOnline"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        numberSensors = data[1]
        sensorsStatus = []
        for x in range(numberSensors):
            sensorsStatus.append(data[2 + 5 * x])
        return sensorsStatus

    """ getFusionValues:
    Returns an array where each element is an array providing the X and Y coordinates of a possible person detection 
    and a value indicating the confidence level that thay is a real person or not.
    
    False is returned in case of connection error
    """

    def getFusionValues(self, wait=True):
        # returns [[centroid X, centroid Y, sensed value]]
        data = self.executeCommand(self.kinseiCommand["fusionValues"], wait)
        if data == self.kinseiCommand["error"]:
            return []
        numberSensedLocations = data[1]
        sensedLocationsData = []
        for i in range(numberSensedLocations):
            locationStatus = []
            x = [data[4 + 7 * i], data[5 + 7 * i]]
            locationStatus.append(self.bytes_to_int(x))
            y = [data[6 + 7 * i], data[7 + 7 * i]]
            locationStatus.append(self.bytes_to_int(y))
            locationStatus.append(data[7 + 7 * i] / 10)
            sensedLocationsData.append(locationStatus)
        return sensedLocationsData

    """ getZones:
    Returns an array with all defines zones of interest.
    Each array will provide a label indicating if the zone is "circular" or "polygonal".
    In case of circular, the X and Y coordinates and the radius will be provides
    In case of polygonal, the X and Y coordinates (in sequence) of each corner will be provided
    
    False is returned in case of connection error
    """

    def getZones(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["zones"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        numberZones = data[1]
        zonesSpecs = []
        indexData = 0
        for x in range(numberZones):
            currentZone = []
            if data[2 + indexData] == 0:
                currentZone.append("circular")
                centreX = [data[3 + indexData], data[4 + indexData]]
                centreY = [data[5 + indexData], data[6 + indexData]]
                radius = [data[7 + indexData], data[8 + indexData]]
                currentZone.append(self.bytes_to_int(centreX))
                currentZone.append(self.bytes_to_int(centreY))
                currentZone.append(self.bytes_to_int(radius))
                indexData += 7
            else:
                currentZone.append("polygonal")
                numberCorners = data[3 + indexData]
                for y in range(numberCorners):
                    cornerX = [data[4 + indexData + 4 * y], data[5 + indexData + 4 * y]]
                    cornerY = [data[6 + indexData + 4 * y], data[7 + indexData + 4 * y]]
                    currentZone.append(self.bytes_to_int(cornerX))
                    currentZone.append(self.bytes_to_int(cornerY))
                indexData += (4 * numberCorners + 1)
            zonesSpecs.append(currentZone)
        return zonesSpecs

    """ executeCommand:
    Executes any comand and return the message from the device at it was received
    
    False is returned in case of connection error
    """

    def executeCommand(self, command, wait=True):
        if self.serverConnected:
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

    """ executeVariableCommand:
    Executes any comand and return the message from the devoce at it was received assiming data size is int he second/third byte
    with data size given by size
    
    False is returned in case of connection error
    """

    def executeVariableCommand(self, command, size=2, wait=True):
        if self.serverConnected:
            try:
                self.server.sendall(command)
                dataSizeByte = self.server.recv(3)
                dataSize = self.bytes_to_int([dataSizeByte[1], dataSizeByte[2]])
                data = self.server.recv(size * dataSize)
                if (wait):
                    time.sleep(self.latencyMS / 1000)
                return data
            except socket.error as err:
                return self.kinseiCommand["error"]
        else:
            return self.kinseiCommand["error"]

    """ getStablePosition:    
    Returns a position, if possible, that is stable for a given ammount of time
    Arguments are as follows:
    
    whichPerson:         which person to be checked
    timeMS:              time interval for stability 
    howManyTries:        maximum number of tries
    """

    def getStablePosition(self, whichPerson=0, timeMS=500, howManyTries=5):
        iterations = math.floor(timeMS / self.latencyMS) + 1
        for i in range(0, howManyTries):
            newPosition = self.getPersonsPositions()[whichPerson]
            stable = True
            for ii in range(0, iterations):
                currentPosition = self.getPersonsPositions()[whichPerson]
                if currentPosition != newPosition:
                    stable = False
                    break
            if stable:
                return newPosition
        return False

    """ getAlStablePositions:    
        Returns all position as either stable for 'frame' number of samples or None
        Arguments are as follows:

        frames:              number of frames with frame periodicity defined by self.latencyMS
        """

    def getAlStablePositions(self, frames=3, wait=True):
        if not self.stablePositions:
            self.stablePositions = self.getPersonsPositions(wait)
            self.stablePositionsFrames = [0] * len(self.stablePositions)
            return self.stablePositions
        else:
            currentPositions = self.getPersonsPositions(wait)
            returnedPositions = []
            for i in range(0, len(currentPositions)):
                deltaPosition = max(abs(currentPositions[i][0] - self.stablePositions[i][0]),
                                    abs(currentPositions[i][1] - self.stablePositions[i][1]))
                if deltaPosition < self.radiusStability:
                    self.stablePositionsFrames[i] += 1
                    if self.stablePositionsFrames[i] == frames:
                        self.stablePositionsFrames[i] = 0
                        returnedPositions.append(currentPositions[i])
                    else:
                        returnedPositions.append(None)
                else:
                    returnedPositions.append(None)
                    self.stablePositionsFrames[i] = 0
                    self.stablePositions[i] = currentPositions[i]
            return returnedPositions

    """ getThermalMapResolution:
    !! useable only from trackingserver july2017 !!
    Returns the number of pixel per x and y axis and the pixel size in mm.
    
    False in case of communication error
    """

    def getThermalMapResolution(self, wait=True):
        data = self.executeCommand(self.kinseiCommand["thermres"], wait)
        if data == self.kinseiCommand["error"]:
            return False
        return [data[1], data[2], data[3]]

    """ getThermalMapPixels:
    !! available only from trackingserver july2017 !!
    Returns the pisel temperatures in row order
    
    False in case of communication error
    """

    def getThermalMapPixels(self, wait=True):
        data = self.executeVariableCommand(self.kinseiCommand["thermmap"], 2, wait)
        numberPixels = math.trunc(len(data) / 2)
        pixelTemps = []
        # transform data into an array of temperatures factored by 10x in integers
        for i in range(numberPixels):
            pixelTemps.append(self.bytes_to_int([data[2 * i], data[2 * i + 1]]))
        return pixelTemps

    """
    Internal methods
    """

    def bytes_to_int(self, bytes):
        result = 0
        for b in bytes:
            result = result * 256 + int(b)
        return result
