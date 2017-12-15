#!/usr/bin/python3

"""KinseiTuner.py: core client for tuning a kinsei system"""

import socket
import time
import math
import struct

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredtrackingserver__ = "july2017 or later"

setCommand = {
    "backgroundAlfa": b'\x02',
    "backgroundThreshold": b'\x04',
    "temperatureThreshold": b'\x06',
    "fusionBackgroundThreshold": b'\x08',
    "fusionConsensumFactor": b'\x0a',
    "fusionThreshold": b'\x0c'
}

getCommand = {
    "backgroundAlfa": b'\x01',
    "backgroundThreshold": b'\x03',
    "temperatureThreshold": b'\x05',
    "fusionBackgroundThreshold": b'\x07',
    "fusionConsensumFactor": b'\x09',
    "fusionThreshold": b'\x0b'
}

orderedKeys = ["backgroundAlfa", "backgroundThreshold", "temperatureThreshold", \
               "fusionBackgroundThreshold", "fusionConsensumFactor", "fusionThreshold"]


class KinseiTuner(object):
    internalCommands = {
        "reset": b'\x00',
        "saveOverride": b'\xfe',
        "deleteOverride": b'\xff',
        "resetOffset": b'\xfd',
        "error": b'\x65'
    }

    """ __init__:
    The costructor create the socket for a device at the provided IP and port.
    
    Arguments are as follows:
    host:             device IP with default value valid for a device in Access Point mode
    timeout:          timeout of the connection in ms
    pauseMS:          interval forced between commands to the device in ms
    port:             device port, 2005 is the default port if not manually changed in the device itself
    """

    def __init__(self, host='192.168.76.1', timeout=15.0, pauseMS=350, port=6666):
        self.latencyMS = pauseMS
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
    Set the time interval between to messages forced when the methods below are executes with the flag wait
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

    """ executeCommand:
    Executes any comand and return the message from the device at it was received
    False is returned in case of connection error
    """

    def exec(self, command, wait=True):
        if self.serverConnected:
            try:
                self.server.sendall(command)
                data = self.server.recv(3)
                if (wait):
                    time.sleep(self.latencyMS / 1000)
                return data
            except socket.error:
                return self.internalCommands["error"]
        else:
            return self.internalCommands["error"]

    """ resetBackground:
    Returns True if the tracking and fusion server has been sucessfully resetted
    False otherwise
    """

    def resetBackground(self, wait=True):
        data = self.exec(self.internalCommands["reset"], wait)
        if data == self.internalCommands["error"]:
            return False
        if data == self.internalCommands["reset"]:
            return True
        return False

    """ resetOffset:
    Returns True if the tracking and fusion server has been sucessfully resetted
    False otherwise
    """

    def resetOffset(self, wait=True):
        data = self.exec(self.internalCommands["resetOffset"], wait)
        if data == self.internalCommands["error"]:
            return False
        if data == self.internalCommands["resetOffset"]:
            return True
        return False

    """ execGet:
    Execute the specified get command and returns the value converted to decimal
    False is returned in case or connection error
    
    For the supported commands refer to "getCommand" dict and the kinsei.tuning.interface.txt documentation
    """

    def execGet(self, command, wait=True):
        data = self.exec(command, wait)
        if data == self.internalCommands["error"]:
            return False
        if command == getCommand["temperatureThreshold"]:
            return (struct.unpack('>h', data[1:3])[0]) / 100
        else:
            return int.from_bytes(data[1:3], byteorder='big') / 100

    """ execSet:
    Execute the specified set command and returns true is succesfull
    False is returned in case or connection error
    
    For the supported commands refer to "setCommand" dict and the kinsei.tuning.interface.txt documentation
    """

    def execSet(self, command, argument, wait=True):
        argument100 = int(argument * 100)
        if math.ceil(argument100.bit_length() / 8) > 2:
            return False
        argumentBytes = struct.pack('>h', argument100)
        command = b"".join([command, argumentBytes])
        data = self.exec(command, wait)
        if data == self.internalCommands["error"]:
            return False
        returnedData = int.from_bytes(data[1:3], byteorder='big') / 100
        return returnedData == argument

    """ readFullConfiguration:
    Returns the current configuraton into an ordered list as form list orderedKeys
    False is returned in case of connection error
    """

    def readFullConfiguration(self):
        configuration = []
        try:
            for i in range(0, len(orderedKeys)):
                configuration.append(self.execGet(getCommand[orderedKeys[i]], False))
            return configuration
        except:
            return False

    """ writeFullConfiguration:
    Write the provided configuraton as an ordered list following the list orderedKeys
    False is returned in case of connection error
    """

    def writeFullConfiguration(self, configData):
        try:
            for i in range(0, len(orderedKeys)):
                self.execSet(setCommand[orderedKeys[i]],configData[i])
            return True
        except:
            return False

    """ saveOveride:
    Save the current configuration as overide in the device
    False is returned in case of connection error
    """

    def saveOveride(self):
        try:
            answer = self.exec(self.internalCommands["saveOverride"])
            return answer == self.internalCommands["saveOverride"]
        except:
            return False

    """ saveOveride:
    Remove the current overide file from the device
    False is returned in case of connection error
    """

    def removeOveride(self):
        try:
            answer = self.exec(self.internalCommands["deleteOverride"])
            return answer == self.internalCommands["deleteOverride"]
        except:
            return False
