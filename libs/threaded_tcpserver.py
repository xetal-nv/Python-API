#!/usr/bin/python3

"""threaded_tcpserver.py: a multi threaded TCP server with blocking clients"""

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "in development"

import socket
import threading as thread
import select
import time

VERBOSE = False


class SocketServer(socket.socket):
    clients = []

    def __init__(self):
        socket.socket.__init__(self)
        # To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(('0.0.0.0', 2005))
        self.listen(5)

    def run(self):
        if VERBOSE:
            print("Server started")
        try:
            self.accept_clients()
        except Exception as ex:
            print(ex)
        finally:
            if VERBOSE:
                print("Server closed")
            for client in self.clients:
                client.close()
            self.close()

    def accept_clients(self):
        inputs = [self]
        outputs = []
        while 1:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                if s is self:
                    (clientsocket, address) = self.accept()
                    # Adding client to clients list
                    self.clients.append(clientsocket)
                    # Client Connected
                    self.onopen(clientsocket)
                    # Receiving data from client
                    thread.Thread(target=self.receive, args=(clientsocket,)).start()
            time.sleep(1000)

    def receive(self, client):
        while 1:
            data = client.recv(1024)
            if data:
                # Message Received
                self.onmessage(client, data)
            else:
                break

        # Removing client from clients list
        self.clients.remove(client)
        # Client Disconnected
        self.onclose(client)
        # Closing connection with client
        client.close()
        # Closing thread

    def broadcast(self, message):
        # Sending message to all clients
        for client in self.clients:
            client.send(message)

    def onopen(self, client):
        pass

    def onmessage(self, client, message):
        pass

    def onclose(self, client):
        pass

#
# class BroadcastedEchoExample(SocketServer):
#     def __init__(self):
#         SocketServer.__init__(self)
#
#     def onmessage(self, client, message):
#         print("Client Sent Message")
#         # Sending message to all clients
#         self.broadcast(message)
#
#     def onopen(self, client):
#         print("Client Connected")
#
#     def onclose(self, client):
#         print("Client Disconnected")
#
#
# def test():
#     server = BroadcastedEchoExample()
#     server.run()


if __name__ == "__main__":
    test()
