#!/usr/bin/python3

"""communication.py: basic example of connecting to a Kinsei system for people tracking"""

import sys
import os

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')
import KinseiClient
from KinseiTuner import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "2.0.2"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "february2017 or later"

# it accespt also DNS addresses

IP_DEVICE = "192.168.0.135" # remove comment to set as default the standard AP address
# IP_DEVICE = "192.168.1.80"  # remove comment to set as default the standard AP address
# IP_DEVICE = "81.82.231.115" # occasionally remotely available Kinsei kit

# Set to false with firmwares older than july2017
FWB4july2017 = True


def start():
    # create a socket connection to the device
    demoKit = KinseiClient.KinseiSocket(IP_DEVICE)

    if FWB4july2017:
        demoKitTuning = KinseiTuner(IP_DEVICE)
        print("\nCurrent settings of the Kinsei system are:\n")
        print("Background Alfa:", demoKitTuning.execGet(getCommand["backgroundAlfa"]))
        print("Background Threshold:", demoKitTuning.execGet(getCommand["backgroundThreshold"]))
        print("Temperature Threshold:", demoKitTuning.execGet(getCommand["temperatureThreshold"]))
        print("Fusion Background Threshold:", demoKitTuning.execGet(getCommand["fusionBackgroundThreshold"]))
        print("Fusion Consensum Factor:", demoKitTuning.execGet(getCommand["fusionConsensumFactor"]))
        print("Fusion Threshold:", demoKitTuning.execGet(getCommand["fusionThreshold"]))
        input("\nPress Enter to continue...")

    # check if the system is online before asking data
    if demoKit.checkIfOnline():
        # get room bounding box dimensions
        dimensions = demoKit.getRoomSize()
        if dimensions:
            print("\nThe Kinsei system is online. \nRoom size is " + str(dimensions[0]) + "mm by " + str(
                dimensions[1]) + "mm.\n")
            print("Starting persons tracking")
            while True:
                # get position data
                positionData = demoKit.getPersonsPositions(False)
                if positionData:
                    print("Coordinates of present persons ")
                    print("\t\t", positionData)
                # get the number of people in float mode
                positionData = demoKit.getNumberPersonsFloat()
                if positionData:
                    print("Number of detected people is " + str(positionData) + "\n")
        else:
            print("There has been an error in communicating with the Kinsei system")
    else:
        print("\nERROR: The Kinsei system has not been found")


if __name__ == "__main__": start()
