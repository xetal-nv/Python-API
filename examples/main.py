#!/usr/bin/python3

"""main.py: main for all examples, please enable only one by selecting the proper item of the availableDemos dictionary"""

import sys
sys.path.insert(0, '../viewers')
from viewers import trackingFusionViewer, thermalmap, communication, trackingViewer, hotspotmap
from servers import presencehttp

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "1.0.1"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"

availableDemos = {
                  # shows an example of communication and tracking, not graphical
                  "communication": communication.start,
                  # shows an example of graphical viewer for tracking
                  "trackingViewer": trackingViewer.start,
                  # shows an example of graphical viewer for tracking and raw data (fusion)
                  "trackingFusionViewer": trackingFusionViewer.start,
                  # shows an example of http server reporting number of people
                  "presencehttp": presencehttp.start,
                  # shows a thermal map based on the settings in the source files
                  "thermalmap": thermalmap.start,
                  # shows a an hot spot map based on people position
                  "hotspotmap": hotspotmap.start
                  }

def main():
    availableDemos["hotspotmap"]()
    
        
if __name__ == "__main__": main()
