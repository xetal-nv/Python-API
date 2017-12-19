
"""guy.py: methods for gui interfaces"""

import os
from tkinter import *
from tkinter import messagebox

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "2.1.3"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "internal usage, not documented"

# name of where the last used ip/dns is saved
SAVEDIP = "../.ip"

# name of where the last used username is saved
SAVEDUSER = "../.username"


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
        # bind enter to accept entry
        master.bind('<Return>', lambda _x: self.connectDevice())

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


# This class is used to get the SSH login informstion of the device from the user
class LoginGUI:
    # not working
    def __init__(self, master, device, platformCheck=True):
        self.master = master
        self.device = device
        self.platformCheck = platformCheck

        # bind escape to terminate
        master.bind('<Escape>', quit)
        # bind enter to accept entry
        master.bind('<Return>', lambda _x: self.connectDevice())

        frameEntry = Frame(self.master)
        frameEntry.pack(padx=20, pady=20)
        frameButtons = Frame(self.master)
        frameButtons.pack(padx=20, pady=20)

        self.master.title("SSH Login")
        self.master.attributes("-topmost", True)

        Label(frameEntry, text="Username").grid(row=0, sticky=E)
        Label(frameEntry, text="Password").grid(row=1, sticky=E)
        Label(frameEntry, text="Device IP").grid(row=2, sticky=E)

        self.username = Entry(frameEntry)
        self.password = Entry(frameEntry, show="*")
        self.hostip = Entry(frameEntry)
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        self.hostip.grid(row=2, column=1)

        if os.path.isfile(SAVEDIP):
            with (open(SAVEDIP, 'r')) as savedIP:
                ip = savedIP.read().strip('\n')
                self.hostip.insert(0, ip)
        else:
            self.hostip.insert(0, "192.168.76.1")

        if os.path.isfile(SAVEDUSER):
            with (open(SAVEDUSER, 'r')) as savedUser:
                name = savedUser.read().strip('\n')
                self.username.insert(0, name)
        else:
            self.username.insert(0, "root")

        if self.platformCheck:
            startingGrid = 3
            Label(frameEntry, text="Kit version").grid(row=startingGrid, column=0, sticky=E)
            self.version = DoubleVar()
            self.version.set(2.1)
            for text, mode in self.device.VERSIONS:
                Radiobutton(frameEntry, text=text, variable=self.version, value=mode).grid(row=startingGrid,
                                                                                           column=1, sticky=W)
                startingGrid += 1

        Button(frameButtons, text='Connect', command=self.connectDevice).grid(row=1, column=0)
        Button(frameButtons, text='Open Editor', command=self.openEditor).grid(row=1, column=2, sticky=E)
        Button(frameButtons, text='Quit', command=master.quit).grid(row=1, column=3, sticky=E)

    def connectDevice(self):
        username = self.username.get()
        password = self.password.get()
        if not password:
            messagebox.showinfo("Null password", "Null password is not supported, please set one before using this tool")
        else:
            hostname = self.hostip.get()

            if self.platformCheck:
                self.device.setPlatform(self.version.get())

            # need to ask which device platform is it

            self.device.connect(username, password, hostname)

            if self.device.isConnected():
                self.master.destroy()
                with (open(SAVEDIP, 'w')) as saved:
                    saved.write(hostname)
                with (open(SAVEDUSER, 'w')) as saved:
                    saved.write(username)
                self.device.start()
            else:
                if messagebox.askokcancel("Connection failed", "Failed to connect or login to the device\n"
                                                               "Proceed anyhow?"):
                    self.master.destroy()
                    self.device.start(False)

    def openEditor(self):
        self.master.destroy()
        self.device.start(False)
