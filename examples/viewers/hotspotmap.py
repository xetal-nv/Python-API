#!/usr/bin/python3

"""hotspotmap.py: graphical viewer for persons tracking and fusion (raw data indicating
    a possible detected person where probability of being a real person is proportional to the color brightness)
    NOTE: that the script does not check if the number of sampled positions exceeds the maximum (float64.max)"""

# import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tkinter import *

sys.path.insert(0, '../../libs')
import KinseiClient
import gui
from colormaps import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.1.1"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in testing"
__requiredfirmware__ = "february2017 or later"

# TODO Turn on experimental mode based on all possible data points
# TODO add outliers removal om max
# please use SKIMSAMPLES > 5 and set a RAWTHRESHOLD to ignore false data points
EXPMODE = True
RAWTHRESHOLD = 10

# Highlight most prominent samples above a give threshold (0.0 - 1.0)
CLEANMIN = 0

# How many samples needs to be skipped, this can be used to dilute aggregation
SKIMSAMPLES = 5


class HotSpotMap:
    def __init__(self):
        self.demoKit = None
        self.connected = False

    def connect(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    def start(self):
        if self.connected:
            # get room bounding box dimensions
            dimensions = self.demoKit.getRoomSize()
            if dimensions:
                dimensions = list(map(lambda x: int(x / SCALE), dimensions))
                heatmapMatrix = np.random.rand(dimensions[1], dimensions[0])

                fig, ax = plt.subplots()
                fig.canvas.set_window_title("Hot Spot Map (SCALE : 1:" + str(SCALE) + " mm)" )
                im = plt.imshow(heatmapMatrix, cmap='inferno', interpolation='nearest')
                plt.colorbar()
                heatmapMatrix = np.zeros((dimensions[1], dimensions[0]))

                def data_gen():
                    positionData = []
                    if EXPMODE:
                        fusionData = self.demoKit.getFusionValues(False)
                        for i in range(0, len(fusionData)):
                            positionData.append([int(fusionData[i][0]/SCALE), int(fusionData[i][1]/SCALE)])
                    else:
                        positionData = self.demoKit.getPersonsPositions(False)
                        if positionData:
                            positionData = list(map(lambda x: [int(x[0] / SCALE), int(x[1] / SCALE)], positionData))
                    for x in positionData:
                        if x != [0, 0]:
                            if (not EXPMODE) or (fusionData[i][2] > RAWTHRESHOLD):
                                heatmapMatrix[x[1]][x[0]] += 1
                    if heatmapMatrix.max() > 0:
                        result = heatmapMatrix / heatmapMatrix.max()
                        result[result <= CLEANMIN] = 0
                        yield result
                    else:
                        yield np.zeros((dimensions[1], dimensions[0]))

                def update(heatmapMatrix):
                    im.set_data(heatmapMatrix)
                    return im

                print("\nThe DemoKit is online. \nRoom size is " + str(dimensions[0] * SCALE / 10) + "cm by " + str(
                    dimensions[1] * SCALE / 10) + "cm.\n")
                print("Starting persons tracking")

                ani = animation.FuncAnimation(fig, update, data_gen, interval=1 + SKIMSAMPLES * self.demoKit.getTimeIntervalMS())

                plt.show()

            else:
                print("There has been an error in communicating with the DemoKit")


def start():
    root = Tk()
    device = HotSpotMap()
    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__": start()
