#!/usr/bin/python3

"""guy.py: methods for gui interfaces"""

import ipaddress
from tkinter import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"


# this class is used to get the IP of the device from the user
class StartGUI:
    def __init__(self, master, device):
        self.master = master
        self.device = device
        master.title("Kinsei Viewer Demo")
        Label(master, text='Insert the device IP').pack(side=TOP, padx=130, pady=10)

        self.ipEntry = Entry(master, width=20)
        self.ipEntry.pack(side=TOP, padx=10, pady=10)
        # self.ipEntry.insert(0,"192.168.42.1") # remove comment to set as default the standard AP address
        # self.ipEntry.insert(0,"192.168.76.1") # remove comment to set as default the standard AP address
        self.ipEntry.insert(0, "81.82.231.115")  # occasionally remotely available Xetal kit

        # bind escape to terminate
        master.bind('<Escape>', quit)

        Button(master, text='Connect IP', command=self.connectDeviceIP).pack(side=LEFT, padx=10, pady=5)
        Button(master, text='Connect DNS', command=self.connectDeviceDNS).pack(side=LEFT, padx=10, pady=5)
        Button(master, text='Quit', command=master.quit).pack(side=RIGHT, padx=10, pady=5)

    def connectDeviceIP(self):
        # the module ip address is used to verify the validity of the entered IP address
        try:
            ipaddress.ip_address(self.ipEntry.get())
        except:
            self.ipEntry.configure(fg="red")
            return

        self.ipEntry.configure(fg="black")
        self.device.connect(self.ipEntry.get())

        if self.device.isConnected():
            self.master.destroy()
            self.device.start()
        else:
            self.ipEntry.configure(fg="red")

    def connectDeviceDNS(self):
        # the module ip address is used to verify the validity of the entered IP address

        self.ipEntry.configure(fg="black")
        self.device.connect(self.ipEntry.get())

        if self.device.isConnected():
            self.master.destroy()
            self.device.start()
        else:
            self.ipEntry.configure(fg="red")
