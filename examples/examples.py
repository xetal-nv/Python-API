#!/usr/bin/python3

"""main.py: main for all examples, please enable only one by selecting the proper item of the availableDemos
dictionary """

import sys, collections, subprocess
import tkinter as tk


sys.path.insert(0, '../libs')

# from analyzers import

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"

availableApps = {
    # starts the device tuner
    "Runtime Tuner": lambda: subprocess.Popen(["python", "./tuners/tuner.py"]),
    # starts the device configurator
    "Configurator": lambda: subprocess.Popen(["python", "./tuners/configurator.py"])
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
