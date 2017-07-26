#!/usr/bin/python3

"""hotspot_viewer.py: graphical viewer for persons tracking and fusion (raw data indicating
    a possible detected person where probability of being a real person is proportional to the color brightness)
    NOTE: It requires an aggregator server"""

import socket
import struct
from tkinter import *

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, '../../libs')
import gui
from colormaps import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.2"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "february2017 or later"

# Aggregator server port
PORT = 9000


class HotSpotMapWithServer:
    def __init__(self):
        self.server = None
        self.connected = False

    def connect(self, ip):
        try:
            # Create a TCP/IP socket
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect the socket to the port where the server is listening
            server_address = (ip, PORT)
            print('Connecting to aggregating server at {} port {}'.format(*server_address))
            self.server.connect(server_address)
            self.connected = True

        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    def start(self):
        if self.connected:
            # get room bounding box dimensions
            message = b'dm'
            self.server.sendall(message)
            data = self.server.recv(4)
            dimension0 = struct.unpack('I', data)[0]
            data = self.server.recv(4)
            dimension1 = struct.unpack('I', data)[0]

            def getDatagetData():
                try:
                    message = b'hm'
                    self.server.sendall(message)
                    size = dimension0 * dimension1
                    d = []
                    for i in range(size):
                        data = self.server.recv(4)
                        value = struct.unpack('f', data)[0]
                        d.append(value)
                    newMatrix = np.array(d).reshape(dimension0, dimension1)
                    return newMatrix
                except:
                    return None

            heatmapMatrix = np.random.rand(dimension0, dimension1)
            fig, ax = plt.subplots()
            fig.canvas.set_window_title("Hot Spot Map (scale: " + str(SCALE) + "mm:1)")
            im = plt.imshow(heatmapMatrix, cmap='inferno', interpolation='nearest')
            plt.colorbar()
            # noinspection PyUnusedLocal
            heatmapMatrix = np.zeros((dimension0, dimension1))

            def data_gen():
                newMatrix = getDatagetData()
                if newMatrix is None:
                    yield np.zeros((dimension0, dimension1))
                    print("error")
                else:
                    yield newMatrix

            def update(heatmapMatrix):
                im.set_data(heatmapMatrix)
                return im

            print("\nThe DemoKit is online. \nRoom size is " + str(dimension0 * SCALE / 10) + "cm by " \
                  + str(dimension1 * SCALE / 10) + "cm.\n")
            print("Starting persons tracking")

            # noinspection PyUnusedLocal
            ani = animation.FuncAnimation(fig, update, data_gen, interval=1000)

            plt.show()


def start():
    root = Tk()
    device = HotSpotMapWithServer()
    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__":
    start()
