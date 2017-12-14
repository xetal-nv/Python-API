#!/usr/bin/python3

"""examples.py: main for all examples"""

import collections
import subprocess
import tkinter as tk
import os

# sys.path.append('../libs')

# from analyzers import

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "2.3.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"

absolutePath = os.path.dirname(__file__)
viewersFolder = 'viewers'
serverFolder = 'servers'
interactiveappsFolder = 'interactiveapps'

availableDemos = {
    # shows an example of graphical viewer for tracking
    "Tracking viewer": lambda: subprocess.Popen(
        ["python3", os.path.join(absolutePath, viewersFolder, 'trackingViewer.py')]),
    # shows an example of graphical viewer for tracking and raw data (fusion)
    "Tracking & fusion viewer": lambda: subprocess.Popen(
        ["python3", os.path.join(absolutePath, viewersFolder, 'trackingFusionViewer.py')]),
    # shows a thermal map based on the settings in the source files
    "Thermal map": lambda: subprocess.Popen(
        ["python3", os.path.join(absolutePath, viewersFolder, 'thermalmap.py')]),
    # shows a an hot spot map based on people position
    "Hotspot map": lambda: subprocess.Popen(
        ["python3", os.path.join(absolutePath, viewersFolder, 'hotspotmap.py')]),
    # shows a an example of drawing by moving
    "Draw by moving": lambda: subprocess.Popen(
        ["python3", os.path.join(absolutePath, interactiveappsFolder, 'drawByMoving.py')]),
    # installation and text application
    "Event Monitor": lambda: subprocess.Popen(
        ["python3", os.path.join(absolutePath, interactiveappsFolder, 'eventmonitor.py')]),
}


def main():
    print(absolutePath)

    orderedAvailableDemos = collections.OrderedDict(sorted(availableDemos.items()))
    root = tk.Tk()
    root.title("Demo Selector")

    # bind escape to terminate
    root.bind('<Escape>', quit)

    frame1 = tk.Frame(root)
    frame1.pack(side=tk.TOP, padx=5, pady=10)
    i = 1
    for name, func in orderedAvailableDemos.items():
        tk.Button(frame1, text=name, command=func, width=20).grid(row=i, padx=5)
        i += 1
    root.mainloop()


if __name__ == "__main__":
    main()
