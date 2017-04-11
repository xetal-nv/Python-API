#!/usr/bin/python3

"""presencehttp.py: basic example of a http server returning the number pf people present (float and fixed)"""

import sys
import datetime

sys.path.insert(0, '../libs')
import KinseiClient
from http.server import BaseHTTPRequestHandler, HTTPServer

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.5.0"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "pre release"
    
PORT_NUMBER = 8080
# in AP mode it is '192.168.42.1' otherwise check your network
# it accespt also DNS addresses
#IP_DEVICE = '192.168.42.1' 
IP_DEVICE = '192.168.1.67' 


class myHandler(BaseHTTPRequestHandler):
    
    def getNumberPersonsPresent(self):
        # create a socket coinnection to the device
        #demoKit2 = KinseiClient.KinseiSocket('192.168.1.42') # change the IP with the one used by the kit
        demoKit2 = KinseiClient.KinseiSocket(IP_DEVICE) # change the IP with the one used by the kit
        # check if the system is online before asking data
        if demoKit2.checkIfOnline():
            numberPeopleFixed = demoKit2.getNumberPersonsFixed()
            numberPeopleFloat = demoKit2.getNumberPersonsFloat()
            return [numberPeopleFixed, numberPeopleFloat]
        return False
        
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
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
    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print ('Started httpserver on port ' + str(PORT_NUMBER))
        
        #Wait forever for incoming htto requests
        server.serve_forever()
    
    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()
        
if __name__ == "__main__": start()

        