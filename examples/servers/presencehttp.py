#!/usr/bin/python3

"""presencehttp.py: basic example of a http server returning the number pf people present (float and fixed)"""

import sys
import datetime
import os

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')
import KinseiClient
from http.server import BaseHTTPRequestHandler, HTTPServer

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "february2017 or later"

PORT_NUMBER = 8080
# IP_DEVICE = "192.168.76.1" # remove comment to set as default the standard AP address
IP_DEVICE = "81.82.231.115"  # occasionally remotely available Xetal kit


class MyHandler(BaseHTTPRequestHandler):
    @staticmethod
    def getNumberPersonsPresent():
        # create a socket coinnection to the device
        demoKit2 = KinseiClient.KinseiSocket(IP_DEVICE)  # change the IP with the one used by the kit
        # check if the system is online before asking data
        if demoKit2.checkIfOnline():
            numberPeopleFixed = demoKit2.getNumberPersonsFixed()
            numberPeopleFloat = demoKit2.getNumberPersonsFloat()
            return [numberPeopleFixed, numberPeopleFloat]
        return False

    # Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # check present people
        presence = self.getNumberPersonsPresent()
        # Send the html message
        self.wfile.write(bytes("<H1>Presence detection</H1>", "utf-8"))
        self.wfile.write(bytes("<br>", "utf-8"))
        self.wfile.write(bytes("Time is " + datetime.datetime.now().strftime("%y-%m-%d %H-%M"), "utf-8"))
        self.wfile.write(bytes("<br>", "utf-8"))
        self.wfile.write(bytes("Device at IP " + IP_DEVICE, "utf-8"))
        self.wfile.write(bytes("<br>", "utf-8"))
        self.wfile.write(bytes("Present persons (Fixed) " + str(presence[0]), "utf-8"))
        self.wfile.write(bytes("<br>", "utf-8"))
        self.wfile.write(bytes("Present persons (Float) " + str(presence[1]), "utf-8"))


def start():
    server = None
    try:
        # Creates a web server and defines the handler to manage the
        # incoming request
        server = HTTPServer(('', PORT_NUMBER), MyHandler)
        print('Started httpserver on port ' + str(PORT_NUMBER))

        # Waits forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        if server is not None:
            server.socket.close()


if __name__ == "__main__":
    start()
