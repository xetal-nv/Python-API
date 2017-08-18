#!/usr/bin/python3

"""deviconfig.py: menu for all available configuration applications """

import collections
import subprocess
import sys
import tkinter as tk
import os

sys.path.append('../libs')

# from analyzers import

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"

absolutePath = os.path.dirname(__file__)
tuneFolder = 'tuners'

availableApps = {
    # starts the device tuner
    "Runtime Tuner": lambda: subprocess.Popen(
        ["python", os.path.join(absolutePath, tuneFolder, 'tuner.py')]),
    # starts the device configurator
    "Configurator": lambda: subprocess.Popen(
        ["python", os.path.join(absolutePath, tuneFolder, 'configurator.py')]),
}


def main():

    orderedAvailableDemos = collections.OrderedDict(sorted(availableApps.items()))
    root = tk.Tk()
    root.title("Configuration utilities")

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
