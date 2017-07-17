#!/usr/bin/python3

"""main.py: main for all examples, please enable only one by selecting the proper item of the availableDemos
dictionary """

import sys, collections
import tkinter as tk
import subprocess

sys.path.insert(0, '../libs')

# from analyzers import

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"

availableDemos = {
    # shows an example of communication and tracking, not graphical
    # "Console data": lambda: subprocess.Popen(["python", "./viewers/communication.py"]),
    # shows an example of graphical viewer for tracking
    "Tracking viewer": lambda: subprocess.Popen(["python", "./viewers/trackingViewer.py"]),
    # shows an example of graphical viewer for tracking and raw data (fusion)
    "Tracking & fusion viewer": lambda: subprocess.Popen(["python", "./viewers/trackingFusionViewer.py"]),
    # shows an example of http server reporting number of people
    "Presence http server": lambda: subprocess.Popen(["python", "./servers/presencehttp.py"]),
    # shows a thermal map based on the settings in the source files
    "Thermal map": lambda: subprocess.Popen(["python", "./viewers/thermalmap.py"]),
    # shows a an hot spot map based on people position
    "Hotspot map": lambda: subprocess.Popen(["python", "./viewers/hotspotmap.py"]),
    # starts the device tuner
    "Tuner GUI": lambda: subprocess.Popen(["python", "./tuners/tuner.py"])
}


def main():

    orderedAvailableDemos = collections.OrderedDict(sorted(availableDemos.items()))
    root = tk.Tk()
    root.title("Demo Selector")

    # bind escape to terminate
    root.bind('<Escape>', quit)

    frame1 = tk.Frame(root)
    frame1.pack(side=tk.TOP, padx=5, pady=10)
    i = 1
    for name, func in orderedAvailableDemos.items():
        tk.Button(frame1, text=name, command=func,  width=20).grid(row=i, padx=5)
        i += 1
    root.mainloop()


if __name__ == "__main__":
    main()
