#!/usr/bin/python3

"""aggregator.py: server that aggregates and transmits data from a kinsei kit"""

import sys
import numpy as np
import socket
import threading as thread
import time
import struct

sys.path.insert(0, '../../libs')
import KinseiClient
from threaded_tcpserver import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in development"
__requiredfirmware__ = "february2017 or later"

IP_DEVICE = "81.82.231.115"  # occasionally remotely available Xetal kit
SCALE = 100
SKIMSAMPLES = 0
PORT = 9000


class AggregatorServer(ThreadedServer):
    def __init__(self, host, port):
        ThreadedServer.__init__(self, host, port)
        self.demoKit = None
        self.connected = False
        self.dataLock = thread.Lock()
        self.hotSpotMatrix = None
        self.size = 0

    def connect(self, ip):
        try:
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    def aggregateData(self):
        if self.isConnected():
            dimensions = self.demoKit.getRoomSize()
            if dimensions:
                dimensions = list(map(lambda x: int(x / SCALE), dimensions))
                self.size = dimensions
                self.hotSpotMatrix = np.zeros((dimensions[0], dimensions[1]))

                def data_gen():
                    while True:
                        positionData = self.demoKit.getPersonsPositions(False);
                        if positionData:
                            positionData = list(map(lambda x: [int(x[0] / SCALE), int(x[1] / SCALE)], positionData))
                        with self.dataLock:
                            for x in positionData:
                                if x != [0, 0]:
                                    self.hotSpotMatrix[x[1]][x[0]] += 1
                            if self.hotSpotMatrix.max() > 0:
                                self.hotSpotMatrix /= self.hotSpotMatrix.max()
                            else:
                                self.hotSpotMatrix = np.zeros((dimensions[0], dimensions[1]))
                        time.sleep(SKIMSAMPLES * self.demoKit.getTimeIntervalMS())

                t = threading.Thread(target=data_gen)
                t.daemon = True
                t.start()

    def onMessage(self, message, client):  # does send anything, but it closes the connection
        if (not self.dataLock.locked()) and (self.hotSpotMatrix is not None):
            # this is enable testing with nc
            if message[-1] == 10:
                message = message[0:-1]
            print("Received ", message, " from ", client)
            if message == b'hm':
                # send matrix dimensions
                # client.send(struct.pack('I', self.size[0]))
                # client.send(struct.pack('I', self.size[1]))
                # send matrix values
                for x in self.hotSpotMatrix.flatten():
                    client.send(struct.pack('f', x))
            elif message == b'dm':
                # send matrix dimensions
                client.send(struct.pack('I', self.size[0]))
                client.send(struct.pack('I', self.size[1]))
            else:
                client.send(b'er')

    def onOpen(self, client, address):
        pass

    def onClose(self, client, address):
        pass


def start():
    aggregatedServer = AggregatorServer('', PORT)
    aggregatedServer.connect(IP_DEVICE)
    if aggregatedServer.isConnected():
        print("Connected")
        aggregatedServer.aggregateData()
        aggregatedServer.listen()
    else:
        print("error")


if __name__ == "__main__": start()
