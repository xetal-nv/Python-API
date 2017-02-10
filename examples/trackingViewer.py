#!/usr/bin/python3

"""trackingViewer.py: basic graphical viewer for persons tracking only"""

from tkinter import *
import sys

sys.path.insert(0, '../libs')
import KinseiClient

__author__      =   "Francesco Pessolano"
__copyright__   =   "Copyright 2017, Xetal nv"
__license__     =   "MIT"
__version__     =   "0.1"
__maintainer__  =   "Francesco Pessolano"
__email__       =   "francesco@xetal.eu"
__status__      =   "release"

def start():
    root = Tk()

    w = Label(root, text="Hello, world!")
    w.pack()
    
    root.mainloop()
    
    
if __name__ == "__main__": start()
