#!/usr/bin/python3

"""main.py: main for all examples, please enable only one by selecting the proper item of the availableDemos dictionary"""

import sys
sys.path.insert(0, '../examples')
import communication
import trackingViewer
import trackingFusionViewer

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "1.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"

availableDemos = {
                  # shows an example of communication and tracking, not graphical
                  "communication": communication.start,
                  "trackingViewer": trackingViewer.start,
                  "trackingFusionViewer": trackingFusionViewer.start
                  }

def main():
    availableDemos["trackingFusionViewer"]()
    
        
if __name__ == "__main__": main()