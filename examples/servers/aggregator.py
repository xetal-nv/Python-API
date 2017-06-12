#!/usr/bin/python3

"""aggregator.py: server that aggregates and broadcast data from a kinsei kit"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sys.path.insert(0, '../../libs')
import KinseiClient

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in development"
__requiredfirmware__ = "february2017 or later"


IP_DEVICE = "81.82.231.115"  # occasionally remotely available Xetal kit
SCALE = 100


def start():
    # create a socket connection to the device
    demoKit2 = KinseiClient.KinseiSocket(IP_DEVICE)
    # check if the system is online before asking data
    if demoKit2.checkIfOnline():
        # get room bounding box dimensions
        dimensions = demoKit2.getRoomSize()
        if dimensions:
            dimensions = list(map(lambda x: int(x / SCALE), dimensions))
            heatmapMatrix = np.random.rand(dimensions[0], dimensions[1])

            fig, ax = plt.subplots()
            fig.canvas.set_window_title("Hot Spot Map")
            im = plt.imshow(heatmapMatrix, cmap='inferno', interpolation='nearest')
            plt.colorbar()
            heatmapMatrix = np.zeros((dimensions[0], dimensions[1]))
            labelX = ['']
            labelX.extend(list(map(lambda x: str(x), range(0, dimensions[0] * SCALE, 5 * SCALE))))
            labelY = ['']
            labelY.extend(list(map(lambda x: str(x), range(0, dimensions[1] * SCALE, 5 * SCALE))))
            ax.set_xticklabels(labelX)
            ax.set_yticklabels(labelY)

            def data_gen():
                positionData = demoKit2.getPersonsPositions(False);
                if positionData:
                    positionData = list(map(lambda x: [int(x[0] / SCALE), int(x[1] / SCALE)], positionData))
                for x in positionData:
                    if x != [0, 0]:
                        heatmapMatrix[x[1]][x[0]] += 1
                if heatmapMatrix.max() > 0:
                    yield heatmapMatrix / heatmapMatrix.max()
                else:
                    yield np.zeros((dimensions[0], dimensions[1]))

            def update(heatmapMatrix):
                im.set_data(heatmapMatrix)
                return im

            print("\nThe DemoKit is online. \nRoom size is " + str(dimensions[0]) + "cm by " + str(
                dimensions[1]) + "cm.\n")
            print("Starting persons tracking")

            ani = animation.FuncAnimation(fig, update, data_gen, interval=350)

            plt.show()

        else:
            print("There has been an error in comunicating with the DemoKit")
    else:
        print("\nERROR: The DemoKit has not been found")


if __name__ == "__main__": start()
