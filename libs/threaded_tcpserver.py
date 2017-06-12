#!/usr/bin/python3

"""threaded_tcpserver.py: a multi threaded TCP server with blocking clients"""

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.5.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in development"

import socket
import threading
import select

# Set verbose for DEBUG ONLY
VERBOSE = True

# Use timeout
TIMEOUT = False
TIMEOUTMS = 60


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()

    def listen(self):
        self.sock.listen(5)
        while True:
            try:
                result = select.select([self.sock], [], [], 0.0)
                if self.sock in result[0]:
                    with self.lock:
                        client, address = self.sock.accept()
                        if TIMEOUT:
                            client.settimeout(TIMEOUTMS)
                        t = threading.Thread(target=self.listenToClient, args=(client, address))
                        t.daemon = True
                        t.start()
            except KeyboardInterrupt:
                break

    def listenToClient(self, client, address):
        size = 1024
        if VERBOSE:
            print("Client connected from ", address)
        self.onConnect(client, address)
        while True:
            try:
                data = client.recv(size)
                if data:
                    self.onMessage(data, client)
                else:
                    if VERBOSE:
                        print("Client from ", address, " disconnected")
                    self.onDisconnect(client, address)
                    client.close()
                    break
            except:
                if VERBOSE:
                    print("Client from ", address, " disconnected")
                self.onDisconnect(client, address)
                client.close()
                break
        return False

    # needs to be properly overridden
    def onMessage(self, message, client):
        if VERBOSE:
            print ("Client ", client, " sent ", message)

    # needs to be properly overridden
    def onConnect(self, client, address):
        pass

    # needs to be properly overridden
    def onDisconnect(self, client, address):
        pass

