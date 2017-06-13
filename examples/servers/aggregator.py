#!/usr/bin/python3

"""aggregator.py: server that aggregates and transmits data from a kinsei kit
    NOTE: it is assumed always the standard port 2005"""

import sys, time, struct, os, re
import numpy as np
import threading as thread

sys.path.insert(0, '../../libs')
import KinseiClient
from threaded_tcpserver import *
from colormaps import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "february2017 or later"

# The kist IP can be specified as a parameter to the command line or here
IP_DEVICE = "81.82.231.115"  # occasionally remotely available Xetal kit

# How many samples needs to be skipped, this cna be used to dilute aggregation
SKIMSAMPLES = 0

# Aggregator server port
PORT = 9000


# Aggregator server class based on the TCP threaded server class ThreadedServer
class AggregatorServer(ThreadedServer):
    def __init__(self, host, port):
        ThreadedServer.__init__(self, host, port)
        self.demoKit = None
        self.connected = False
        self.dataLock = thread.Lock()
        self.hotSpotMatrix = None
        self.size = 0
        self.dimensions = [0, 0]

    def connect(self, ip):
        try:
            print("Connecting to kinsei kit at " + str(ip))
            self.demoKit = KinseiClient.KinseiSocket(ip)
            self.connected = self.demoKit.checkIfOnline()
            self.dimensions = self.demoKit.getRoomSize()
            if self.dimensions:
                self.dimensions = list(map(lambda x: int(x / SCALE), self.dimensions))
                self.size = self.dimensions
                self.hotSpotMatrix = np.zeros((self.dimensions[0], self.dimensions[1]))
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    def aggregateData(self):
        def data_gen():
            while True and (self.hotSpotMatrix.max() < np.finfo('d').max):
                positionData = self.demoKit.getPersonsPositions(False);
                if positionData:
                    positionData = list(map(lambda x: [int(x[0] / SCALE), int(x[1] / SCALE)], positionData))
                with self.dataLock:
                    for x in positionData:
                        if x != [0, 0]:
                            self.hotSpotMatrix[x[1]][x[0]] += 1.0

                            # if self.hotSpotMatrix.max() > 0:
                            #     self.hotSpotMatrix /= self.hotSpotMatrix.max()
                            # else:
                            #     self.hotSpotMatrix = np.zeros((self.dimensions[0], self.dimensions[1]))
                time.sleep(SKIMSAMPLES * self.demoKit.getTimeIntervalMS())
            print("AggregateData terminated at iteration " + str(self.hotSpotMatrix.max()))
            nameFile = str(time.time()) + ".log"
            print("Latest aggregated data saved to file " + nameFile)
            np.savetxt(nameFile, self.hotSpotMatrix)
            # noinspection PyProtectedMember
            os._exit(1)

        t = threading.Thread(target=data_gen)
        t.daemon = True
        t.start()

    def onMessage(self, message, client):  # does send anything, but it closes the connection
        if (not self.dataLock.locked()) and (self.hotSpotMatrix is not None):
            # this is enable testing with nc
            if message[-1] == 10:
                message = message[0:-1]
            # print("Received ", message, " from ", client)
            if message == b'hm':
                # send matrix dimensions
                # client.send(struct.pack('I', self.size[0]))
                # client.send(struct.pack('I', self.size[1]))
                # send matrix values
                if self.hotSpotMatrix.max() > 0:
                    matrix = self.hotSpotMatrix / self.hotSpotMatrix.max()
                else:
                    matrix = np.zeros((self.dimensions[0], self.dimensions[1]))
                for x in matrix.flatten():
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
    candidateIP = IP_DEVICE
    if len(sys.argv) == 2:
        re_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        candidateIP = sys.argv[1]
        if not re_ip.match(candidateIP):
            print("The IP provided is invalid")
            # noinspection PyProtectedMember
            os._exit(1)
    elif len(sys.argv) > 2:
        print("Too many arguments")
        # noinspection PyProtectedMember
        os._exit(1)
    aggregatedServer = AggregatorServer('', PORT)
    aggregatedServer.connect(candidateIP)
    if aggregatedServer.isConnected():
        print("Connected")
        aggregatedServer.aggregateData()
        aggregatedServer.listen()
    else:
        print("Failed to connect to IP " + candidateIP)


if __name__ == "__main__": start()
