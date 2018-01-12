#!/usr/bin/python3

"""communication.py: basic example of connecting to a Kinsei system for people tracking"""

import sys
import os
import re

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')
import KinseiClient
from KinseiTuner import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "2.1.2"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredtrackingserver__ = "february2017 or later"


# Set to false with trackingservers older than july2017
FWB4july2017 = True

def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))


def start():
    # create a socket connection to the device

    ipDevice = input("Please enter the device IP: ")

    connectDevice = True

    if not is_valid_ip(ipDevice):
        ddnsDevice = input("The IP is not valid, is this its DDNS (yes/no)?")
        if ddnsDevice != "yes":
            connectDevice = False

    if connectDevice:
        demoKit = KinseiClient.KinseiSocket(ipDevice)

        if FWB4july2017 and demoKit.checkIfOnline():
            demoKitTuning = KinseiTuner(ipDevice)
            print("\nCurrent settings of the Kinsei system are:\n")
            backgroundAlfa = demoKitTuning.execGet(getCommand["backgroundAlfa"])
            if backgroundAlfa:
                print("Background Alfa:", backgroundAlfa)
                print("Background Threshold:", demoKitTuning.execGet(getCommand["backgroundThreshold"]))
                print("Temperature Threshold:", demoKitTuning.execGet(getCommand["temperatureThreshold"]))
                print("Fusion Background Threshold:", demoKitTuning.execGet(getCommand["fusionBackgroundThreshold"]))
                print("Fusion Consensum Factor:", demoKitTuning.execGet(getCommand["fusionConsensumFactor"]))
                print("Fusion Threshold:", demoKitTuning.execGet(getCommand["fusionThreshold"]))
            else:
                print("Either the tunig server is not active or the port has been blocked")
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

                    # Please comment the code below with __requiredtrackingserver__ older then January 2018
                    # START
                    sensorTemoeratures = demoKit.getSensorTemperatures(False)
                    if sensorTemoeratures:
                        print("Sensor report temperatures ", ' '.join([str(item) for item in sensorTemoeratures]))
                    # END
            else:
                print("There has been an error in communicating with the Kinsei system")
        else:
            print("\nERROR: The Kinsei system has not been found")

    else:
        print("The provided IP", ipDevice, "is not valid")


if __name__ == "__main__": start()
