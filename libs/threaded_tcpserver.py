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

# Set verbose for debug
VERBOSE = False


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(client, address)).start()

    def listenToClient(self, client, address):
        size = 1024
        if VERBOSE:
            print("Client connected from ", address)
        self.onConnect(client, address)
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the received data
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
        client.send(message)

    # needs to be properly overridden
    def onConnect(self, client, address):
        pass

    # needs to be properly overridden
    def onDisconnect(self, client, address):
        pass


def test():
    while True:
        port_num = input("Port? ")
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('', port_num).listen()


if __name__ == "__main__":
    test()
