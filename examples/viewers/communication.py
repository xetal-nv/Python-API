#!/usr/bin/python3

"""communication.py: basic example of connecting to a Kinsei system for people tracking"""

import sys
import os
import re
import time
import datetime

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
    logMode = input("Log mode (y/n)? ")

    if logMode.upper() == 'Y':
        logMode = True
        timeLog = input("Logging activity for how many minutes: ")
        timeLog = round(int(timeLog)*60)
        fileName = input("Log file name? ")
        file = open(fileName, 'w')
    else:
        logMode = False


    connectDevice = True

    if not is_valid_ip(ipDevice):
        ddnsDevice = input("The IP is not valid, is this its DDNS (yes/no)?")
        if ddnsDevice != "yes":
            connectDevice = False

    if connectDevice:
        demoKit = KinseiClient.KinseiSocket(ipDevice)

        if not logMode:
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
                    print("Either the tuning server is not active or the port has been blocked")
                if not logMode: input("\nPress Enter to continue...")

        # check if the system is online before asking data
        if demoKit.checkIfOnline():
            # get room bounding box dimensions
            dimensions = demoKit.getRoomSize()
            if dimensions:
                print("\nThe Kinsei system is online. \nRoom size is " + str(dimensions[0]) + "mm by " + str(
                    dimensions[1]) + "mm.\n")
                print("Starting persons tracking\n")
                if logMode:
                    file.write("# Data spatial range limited to room dimensions " + str(dimensions[0]) + "mm by " + str(
                        dimensions[1]) + "mm.\n")
                    file.write("# Data logged with format timestamp - [position in mm] - number_of_people - [sensor "
                               "temperatures in C]\n\n")
                start_time = time.time()
                while (not logMode) or (timeLog > time.time() - start_time):
                    # get position data
                    positionDataFix = demoKit.getPersonsPositions(False)
                    positionDataFloat = demoKit.getNumberPersonsFloat(False)
                    sensorTemperatures = demoKit.getSensorTemperatures(False)
                    if not logMode:
                        if positionDataFix:
                            print("Coordinates of present persons ")
                            print("\t\t", positionDataFix)
                        # get the number of people in float mode
                        if positionDataFloat or positionDataFloat == 0.0:
                            print("Number of detected people is " + str(positionDataFloat) + "\n")

                        # Please comment the code below with trackingserver older then January 2018
                        # START
                        if sensorTemperatures:
                            print("Sensor report temperatures ", ' '.join([str(item) for item in sensorTemperatures]))
                        # END
                    else:
                        file.write(str(datetime.datetime.time(datetime.datetime.now())) + ' - ')
                        if positionDataFix:
                            file.write('[ ')
                            for pos in positionDataFix:
                                file.write('[' + str(pos[0]) + ', ' + str(pos[1]) + '] ')
                            file.write('] - ')
                        # get the number of people in float mode
                        if positionDataFloat or positionDataFloat == 0.0:
                            file.write(str(positionDataFloat) + " - ")
                        # Please comment the code below with tracking server older then January 2018
                        # START
                        if sensorTemperatures:
                            file.write('[ ' + ', '.join([str(item) for item in sensorTemperatures]) + ']\n')
                        # END
                if logMode: file.close()

            else:
                print("There has been an error in communicating with the Kinsei system")
        else:
            print("\nERROR: The Kinsei system has not been found")

    else:
        print("The provided IP", ipDevice, "is not valid")


if __name__ == "__main__": start()
