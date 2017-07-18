#!/usr/bin/python3

"""guy.py: methods for gui interfaces"""

import os
from tkinter import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.1.1"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"

# name of where the last used ip/dns is saved
SAVEDIP = "../.ip"


# this class is used to get the IP of the device from the user
class StartGUI:
    def __init__(self, master, device):
        self.master = master
        self.device = device
        master.title("Connect to a Kinsei device")
        self.master.attributes("-topmost", True)
        Label(master, text='Insert the device IP').pack(side=TOP, padx=130, pady=10)

        self.ipEntry = Entry(master, width=20)
        self.ipEntry.pack(side=TOP, padx=10, pady=10)
        if os.path.isfile(SAVEDIP):
            with (open(SAVEDIP, 'r')) as savedIP:
                ip = savedIP.read().strip('\n')
                self.ipEntry.insert(0, ip)
        else:
            self.ipEntry.insert(0, "192.168.76.1")

        # bind escape to terminate
        master.bind('<Escape>', quit)

        Button(master, text='Connect', command=self.connectDevice).pack(side=LEFT, padx=10, pady=5)
        Button(master, text='Quit', command=master.quit).pack(side=RIGHT, padx=10, pady=5)

    def connectDevice(self):

        self.ipEntry.configure(fg="black")
        ip = self.ipEntry.get()
        self.device.connect(ip)

        if self.device.isConnected():
            self.master.destroy()
            with (open(SAVEDIP, 'w')) as savedIP:
                savedIP.write(ip)
            self.device.start()
        else:
            self.ipEntry.configure(fg="red")
