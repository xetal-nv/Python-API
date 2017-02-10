#!/usr/bin/python3

"""main.py: basic example of connecting to a Kinsei DemoKit v2 for people tracking"""

import sys

sys.path.insert(0, '../libs')
import KinseiClient

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "1.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"
    
def start():
    # create a socket coinnection to the device
    demoKit2 = KinseiClient.KinseiSocket('81.82.231.115'); # change the IP with the one used by the kit
    # check if the system is online before asking data
    if demoKit2.checkIfOnline():
        # get room boundig box dimensions
        dimensions = demoKit2.getRoomSize()
        if dimensions:
            print("\nThe DemoKit is online. \nRoom size is " + str(dimensions[0]) + "mm by " + str(dimensions[1]) + "mm.\n")
            print("Starting persons tracking")
            while(1):
                # get position data
                positionData = demoKit2.getPersonsPositions(False);
                if positionData:
                    print ("Coordinates af present persons ")
                    print ("\t\t", positionData)
                # get the number of people in float mode
                positionData = demoKit2.getNumberPersonsFloat()
                if positionData:
                    print ("Number of detected people is " + str(positionData) + "\n")
        else:
            print("There has been an error in comunicating with the DemoKit")
    else:
        print("\nERROR: The DemoKit has not been found")
        