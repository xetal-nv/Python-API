#!/usr/bin/python3

"""tuner.py: graphical interface for real-time tuning of the paramenters"""

import sys
import os
import time

absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')
from KinseiTuner import *
import gui
from tooltip import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import *

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.1.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "july2017 or later"

# tips for commands

BA = "Indicates the minimum difference between the background and the measured temperature in order to " \
     "assume there is a person at the measurement location"
BT = "Represents the weight of the new background temperature versus the old one when caculating the new " \
     "background temperature"
TT = "Represents the minimum background temperature with the respect to the average room temperature"
FBT = "This threshold must be high enough to clean the fusion. Increase to reduce noise, decrease to increase samples"
FCF = "The higher the value, the greater priority is given to positions detected by more sensors"
FT = "The position temperature and the background must have a difference greater this threshold" \
     "to be considered a person position candidate"

SEND = "Sends the edited configuration to the device"
FREEZE = "Stores the current configuration as start override"
UNFREEZE = "Removes current start override, resetting to factory default"
BGRESET = "Reset the temperature background"
OFFRESET = "Reset offset of all sensors for hardware calibration (NOTE: offset persist also after turning off/on)"
DISCARD = "Discards all local change made from application start"


# Support functions
def popUpOk(showMessage):
    if showMessage:
        messagebox.showinfo("Information", "Operation was succesfull")


def popUpNotOk():
    messagebox.showinfo("Error", "Operation has failed")


# It implements the graphical interface for the tuner application
class TunerGui:
    def __init__(self):
        self.demoKit = None
        self.ip = None
        self.connected = False
        self.canvas = None
        self.config = None
        self.master = None
        self.scales = []
        self.showMessage = True
        self.autoSend = False
        self.bSend = None


    def connect(self, ip):
        try:
            self.demoKit = KinseiTuner(ip)
            self.connected = self.demoKit.serverConnected
            self.config = self.demoKit.readFullConfiguration()
            self.ip = ip
        except:
            self.connected = False

    def isConnected(self):
        return self.connected

    # this function sets up the canvas and its functions
    def start(self):

        if self.connected:
            self.master = Tk()
            self.master.title("Kinsei Tuner Demo: " + self.ip)

            # bind escape to terminate
            self.master.bind('<Escape>', quit)

            menubar = Menu(self.master)
            filemenu = Menu(menubar, tearoff=0)
            filemenu.add_command(label="Load", command=self.loadConfig)
            filemenu.add_command(label="Save", command=self.saveConfig)
            filemenu.add_separator()
            filemenu.add_command(label="Toggle success messages", command=self.toggleMessages)
            filemenu.add_command(label="Toggle Auto send", command=self.toggleAutoSend)
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=self.master.quit)

            menubar.add_cascade(label="File", menu=filemenu)

            self.master.config(menu=menubar)

            frameSliders = Frame(self.master)
            frameButtons = Frame(self.master)
            frameSliders.pack(padx=20, pady=20)
            frameButtons.pack(padx=20, pady=20)

            wraplength = 200

            labelBA = Label(frameSliders, text="Background Alfa")
            labelBA.grid(row=1, column=0, sticky=E, padx=5)
            backgroundAlfa = Scale(frameSliders, orient=HORIZONTAL, length=450, width=20, digits=3, \
                                   from_=0.1, to=1.0, resolution=0.01)
            backgroundAlfa.grid(row=1, column=3)
            backgroundAlfa.set(self.config[0])
            backgroundAlfa.bind("<ButtonRelease-1>", self.printValues)
            self.scales.append(backgroundAlfa)
            Tooltip(labelBA, text=BA, wraplength=wraplength)

            labelBT = Label(frameSliders, text="Background Threshold")
            labelBT.grid(row=2, column=0, sticky=E, padx=5)
            backgroundThreshold = Scale(frameSliders, orient=HORIZONTAL, length=450, width=20, digits=4, \
                                        from_=0.1, to=10.0, resolution=0.01)
            backgroundThreshold.grid(row=2, column=3)
            backgroundThreshold.set(self.config[1])
            backgroundThreshold.bind("<ButtonRelease-1>", self.printValues)
            self.scales.append(backgroundThreshold)
            Tooltip(labelBT, text=BT, wraplength=wraplength)

            labelTT = Label(frameSliders, text="Temperature Threshold")
            labelTT.grid(row=3, column=0, sticky=E, padx=5)
            temperatureThreshold = Scale(frameSliders, orient=HORIZONTAL, length=450, width=20, digits=4, \
                                         from_=-10.0, to=10.0, resolution=0.01)
            temperatureThreshold.grid(row=3, column=3)
            temperatureThreshold.set(self.config[2])
            temperatureThreshold.bind("<ButtonRelease-1>", self.printValues)
            self.scales.append(temperatureThreshold)
            Tooltip(labelTT, text=TT, wraplength=wraplength)

            labelFBT = Label(frameSliders, text="Fusion Background Threshold")
            labelFBT.grid(row=4, column=0, sticky=E, padx=5)
            fusionBackgroundThreshold = Scale(frameSliders, orient=HORIZONTAL, length=450, width=20, digits=4, \
                                              from_=0.1, to=10.0, resolution=0.01)
            fusionBackgroundThreshold.grid(row=4, column=3)
            fusionBackgroundThreshold.set(self.config[3])
            fusionBackgroundThreshold.bind("<ButtonRelease-1>", self.printValues)
            self.scales.append(fusionBackgroundThreshold)
            Tooltip(labelFBT, text=FBT, wraplength=wraplength)

            labelFCF = Label(frameSliders, text="Fusion Consensum Factor")
            labelFCF.grid(row=5, column=0, sticky=E, padx=5)
            fusionConsensumFactor = Scale(frameSliders, orient=HORIZONTAL, length=450, width=20, digits=3, \
                                          from_=0.1, to=5.0, resolution=0.01)
            fusionConsensumFactor.grid(row=5, column=3)
            fusionConsensumFactor.set(self.config[4])
            fusionConsensumFactor.bind("<ButtonRelease-1>", self.printValues)
            self.scales.append(fusionConsensumFactor)
            Tooltip(labelFCF, text=FCF, wraplength=wraplength)

            labelFT = Label(frameSliders, text="Fusion Threshold")
            labelFT.grid(row=6, column=0, sticky=E, padx=5)
            fusionThreshold = Scale(frameSliders, orient=HORIZONTAL, length=450, width=20, digits=4,
                                    from_=0.1, to=10.0, resolution=0.01)
            fusionThreshold.grid(row=6, column=3)
            fusionThreshold.set(self.config[5])
            fusionThreshold.bind("<ButtonRelease-1>", self.printValues)
            self.scales.append(fusionThreshold)
            Tooltip(labelFT, text=FT, wraplength=wraplength)

            self.bSend = Button(frameButtons, text='SEND', width=8, command=self.sendConfig)
            self.bSend.pack(side=LEFT, padx=5, pady=5)
            Tooltip(self.bSend, text=SEND, wraplength=wraplength)

            bFreeze = Button(frameButtons, text='FREEZE', width=8, command=self.freezeConfig)
            bFreeze.pack(side=LEFT, padx=5, pady=5)
            Tooltip(bFreeze, text=FREEZE, wraplength=wraplength)

            bUnfreeze = Button(frameButtons, text='UNFREEZE', width=8, command=self.unfreezeConfig)
            bUnfreeze.pack(side=LEFT, padx=5, pady=5)
            Tooltip(bUnfreeze, text=UNFREEZE, wraplength=wraplength)

            bBgreset = Button(frameButtons, text='BGRESET', width=8, command=self.bgReset)
            bBgreset.pack(side=LEFT, padx=5, pady=5)
            Tooltip(bBgreset, text=BGRESET, wraplength=wraplength)

            offReset = Button(frameButtons, text='OFFSETRST', width=8, command=self.offsetReset)
            offReset.pack(side=LEFT, padx=5, pady=5)
            Tooltip(offReset, text=OFFRESET, wraplength=wraplength)

            bDiscard = Button(frameButtons, text='DISCARD', width=8, command=self.discard)
            bDiscard.pack(side=LEFT, padx=5, pady=5)
            Tooltip(bDiscard, text=DISCARD, wraplength=wraplength)

    def printValues(self, notUsed):
        if self.autoSend:
            for i in range(0, len(self.config)):
                self.scales[i].config(state=DISABLED)
            self.sendConfig(False)
            for i in range(0, len(self.config)):
                self.scales[i].config(state=NORMAL)

    # The following method toggles on or off the messages
    def toggleMessages(self):
        self.showMessage = not self.showMessage

    # The following method toggles on or off the automatic change send
    def toggleAutoSend(self):
        self.autoSend = not self.autoSend
        if self.autoSend:
            self.bSend.config(state=DISABLED)
        else:
            self.bSend.config(state=NORMAL)


    # The following methods managing device configuration using the KinseiTuner API

    def sendConfig(self, message=True):  # check negatives again!
        newConfig = []
        for i in range(0, len(self.config)):
            newConfig.append(self.scales[i].get())
        if self.demoKit.writeFullConfiguration(newConfig):
            if message:
                popUpOk(self.showMessage)
        else:
            popUpNotOk()

    def saveConfig(self):
        self.master.filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                            filetypes=(("config files", "*.cfg"), ("all files", "*.*")))
        with (open(self.master.filename, 'w')) as saveFile:
            for i in range(0, len(self.scales)):
                saveFile.write(str(self.scales[i].get()) + "\n")

    def loadConfig(self):
        self.master.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                          filetypes=(("config files", "*.cfg"), ("all files", "*.*")))
        with (open(self.master.filename, 'r')) as loadFile:
            for i in range(0, len(self.scales)):
                data = float(loadFile.readline().strip('\n'))
                self.scales[i].set(data)

    def discard(self):
        for i in range(0, len(self.config)):
            self.scales[i].set(self.config[i])
        if self.autoSend:
            for i in range(0, len(self.config)):
                self.scales[i].config(state=DISABLED)
            self.sendConfig(False)
            for i in range(0, len(self.config)):
                self.scales[i].config(state=NORMAL)

    def bgReset(self):
        if messagebox.askyesno('Reset Background', "Make sure nobody is in front of the device. Continue?", \
                               icon=messagebox.QUESTION, default=messagebox.YES):
            if self.demoKit.resetBackground():
                popUpOk(self.showMessage)
            else:
                popUpNotOk()

    def offsetReset(self):
        if messagebox.askyesno('Reset Sensors \' Offsets',
                               'Make sure no predominant heat source is in front of the device. Continue?', \
                               icon=messagebox.QUESTION, default=messagebox.YES):
            if self.demoKit.resetOffset():
                popUpOk(self.showMessage)
            else:
                popUpNotOk()

    def freezeConfig(self):  # wait new fw
        if self.demoKit.saveOveride():
            popUpOk(self.showMessage)
        else:
            popUpNotOk()

    def unfreezeConfig(self):  # wait new fw
        if self.demoKit.removeOveride():
            popUpOk(self.showMessage)
        else:
            popUpNotOk()


def start():
    root = Tk()
    device = TunerGui()
    gui.StartGUI(root, device)
    root.mainloop()


if __name__ == "__main__":
    start()
