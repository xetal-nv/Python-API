#!/usr/bin/python3

"""configurator.py: allows reading and editing of the configuration file; stopping, starting and restarting
    of the kinsei server on the device """

from tkinter import *
from tkinter.scrolledtext import *
from tkinter import filedialog
from tkinter import messagebox
import os
import sys
import platform


absolutePath = os.path.abspath(__file__)
processRoot = os.path.dirname(absolutePath)
os.chdir(processRoot)
sys.path.insert(0, '../../libs')
from KinseiSSHclient import *
import gui

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.3.7"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredtrackingserver__ = "july2017 or later"

# This DICT holds the available configuration commands with type and range
# 'name parameter' : [range type, min, max]
parameters = {
    'CHANNEL': ['num', 0, None],
    'MONITORED_AREA': [None, None, None],
    'SAMPLES_AVERAGE': ['num', 1, None],
    'NOTMONITORED_CZONE': ['', None, None],
    'TRACKING_CONSENSUM_FACTOR': ['num', 0, None],
    'TRACKING_HIGH_FALLBACK_DELAY': ['num', 0, None],
    'COMPORT': [None, None, None],
    'TRACKING_LOW_FALLBACK_DELAY': ['num', 0, None],
    'BACKGROUND_THRESHOLD': ['num', 0, None],
    'ONLINE': ['bool', 0, 1],
    'SAVE_VALUES': ['bool', 0, 1],
    'FUSION_BACKGROUND_THRESHOLD': ['num', 0, None],
    'TRACKING_PERSON_MAXSPEED': ['num', 0, None],
    'TRACKING_FALLBACK_TH_UP': ['num', 0, None],
    'NSENS': ['num', 2, 10],
    'TRACKING_EDGE_DISTANCE': ['num', 0, None],
    'TRACKING_MAX_#PERSONS': ['num', 0, None],
    'TRACKING_MIN_DISTANCE_PERSONS': ['num', 0, None],
    'SEN': [None, 2, None],
    'FUSION_THRESHOLD': ['num', 0, None],
    'THERMALMAP': ['bool', 0, 1],
    'FUSION_BACKGROUND_MAX_TEMP': ['num', 0, None],
    'BACKGROUND_RESET_DELAY': ['num', 0, None],
    'FUSION_CONSENSUM_FACTOR': ['num', 0, 1],
    'TRACKING_MODE': ['bool', 0, 1],
    'BACKGROUND_ALFA': ['num', 0, 1],
    'BACKGROUND_TEMPERATURE_THRESHOLD': ['num', -10, +10],
    'SENSORANGLE_NR': ['set', 'NR', None],
    'CONFIG_SERVERPORT': ['num', 0, None],
    'SENSOR_SAMPLING': ['num', 110, None],
    'SERVERPORT': ['num', 0, None],
    'TRACKING_FALLBACK': [1, 0, 1],
    'TRACKING_FALLBACK_TH_DOWN': ['num', 0, None],
    'NOTMONITORED_PZONE': [None, None, None],
    'PZONE': [None, None, None],
    'CZONE': [None, None, None],
    'TRACKING_AVERAGE': ['num', 1, None]
}

# This DICT holds the colors for syntax highlight
tags = {
    'comment': 'slate gray',
    'command': 'blue',
    'syntaxerror': 'red',
    'valuerror': 'magenta2'
}


# This class creates and manages the configurator GUI and operations
class Configurator:
    VERSIONS = [
        ("<2.0", 2.0),
        (">2.0", 2.1),
    ]

    def __init__(self):
        self.ssh = None
        self.connected = False
        self.root = None
        self.toolmenu = None
        self.configEditor = None
        self.platform = 2.1
        self.showMessage = True

    def __del__(self):
        if self.ssh is not None:
            self.ssh.disconnect()

    # set platform type

    def setPlatform(self, type):
        self.platform = type

    # creates the SSH connection
    def connect(self, username, password, hostname):
        try:
            self.ssh = KinseiSSHclient(username, password, hostname)
            self.connected = self.ssh.connected
        except:
            print("ee")
            self.connected = False

    def isConnected(self):
        return self.connected

    # creates the GUI
    def start(self, connected=True):
        self.root = Tk()
        self.root.title("Kinsei Configuration Editor")
        self.root.resizable(width=True, height=True)

        # bind escape to terminate
        self.root.bind('<Escape>', self.exit)

        # bind any key to colorize and highlight the current line
        self.root.bind('<Key>', self.highlight)

        # make and set the configurator editor GUI
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new)
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="Verify", command=self.verify)
        filemenu.add_separator()
        filemenu.add_command(label="Toggle success messages", command=self.toggleMessages)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)
        self.toolmenu = Menu(menu)
        if connected:
            menu.add_cascade(label="Device Controls", menu=self.toolmenu)
            self.toolmenu.add_command(label="Connect", command=self.forceConnect)
            self.toolmenu.add_command(label="Disconnect", command=self.forceDisconnect)
            self.toolmenu.add_separator()
            self.toolmenu.add_command(label="Read configuration", command=self.readConfig)
            self.toolmenu.add_command(label="Send configuration", command=self.sendConfig)
            self.toolmenu.add_command(label="Send configuration and restart", command=self.sendConfigRestart)
            self.toolmenu.add_separator()
            self.toolmenu.add_command(label="Restart service", state=DISABLED, command=self.restartService)
            self.toolmenu.add_command(label="Stop service", state=DISABLED, command=self.stopService)
            self.toolmenu.add_command(label="Start service", state=DISABLED, command=self.startService)
            self.toolmenu.add_separator()
            self.toolmenu.add_command(label="Upload new trackingserver", state=DISABLED)
            self.toolmenu.add_command(label="Reboot device", state=DISABLED)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.about)

        self.configEditor = ScrolledText(self.root, heigh=30, width=100)
        self.configEditor.pack(fill=BOTH, expand=True)

        # set for highlighting the current line and coloring
        self.configEditor.tag_configure("current_line", background="#e9e9e9")
        self.configEditor.tag_configure("order_error", background="yellow")
        self.config_tags()

        if connected:
            self.setDeviceTools(self.ssh.connected)

    # The following method toggles on or off the messages
    def toggleMessages(self):
        self.showMessage = not self.showMessage

    # The following methods are used for syntax highlight and current line coloring
    def config_tags(self):
        for tag, val in tags.items():
            self.configEditor.tag_config(tag, foreground=val)

    def remove_tags(self, start, end):
        for tag in self.configEditor.tags.keys():
            self.configEditor.tag_remove(tag, start, end)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        start = self.configEditor.index(start)
        end = self.configEditor.index(end)
        self.configEditor.mark_set("matchStart", start)
        self.configEditor.mark_set("matchEnd", start)
        self.configEditor.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.configEditor.search(pattern, "matchEnd", "searchLimit",
                                             count=count, regexp=regexp)
            if index == "":
                break
            if count.get() == 0:
                break  # degenerate pattern which matches zero-length strings
            self.configEditor.mark_set("matchStart", index)
            self.configEditor.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.configEditor.tag_add(tag, "matchStart", "matchEnd")

    def colorizeLine(self, line):
        if line is not '':
            line.strip()
            if line[0] == '#':
                self.configEditor.tag_add('comment', "insert linestart", "insert lineend+1c")
            else:
                confLineData = line.split('=')
                # check for syntax error
                if confLineData[0] not in parameters:
                    self.highlight_pattern(line.split('=')[0], 'syntaxerror',"insert linestart", "insert lineend+1c")
                else:
                    # check for value error
                    error = self.checkForValueErrorInLine(confLineData)
                    if error:
                        color = 'command'
                    else:
                        color = 'valuerror'
                    self.configEditor.tag_add(color, "insert linestart", "insert lineend+1c")

    def highlight(self, _unused):
        self.configEditor.tag_remove("current_line", 1.0, "end")
        for tag in tags:
            self.configEditor.tag_remove(tag, "insert linestart", "insert lineend")
        self.configEditor.tag_add("current_line", "insert linestart", "insert lineend+1c")
        line = self.configEditor.get("insert linestart", "insert lineend")
        self.colorizeLine(line)
        # try to make a full scan since the config file is small enough
        # HERE

    # enables or disables device tools depending on the connection state
    def setDeviceTools(self, flag):
        if flag:
            enabled = 'normal'
            self.toolmenu.entryconfig("Connect", state='disabled')
        else:
            enabled = 'disabled'
            self.toolmenu.entryconfig("Connect", state='normal')
        self.toolmenu.entryconfig("Disconnect", state=enabled)
        self.toolmenu.entryconfig("Read configuration", state=enabled)
        self.toolmenu.entryconfig("Send configuration", state=enabled)
        self.toolmenu.entryconfig("Send configuration and restart", state=enabled)
        self.toolmenu.entryconfig("Restart service", state=enabled)

        # needed to accomodate for hardware platform changes
        if self.platform == 2.1:
            self.toolmenu.entryconfig("Stop service", state=enabled)
            self.toolmenu.entryconfig("Start service", state=enabled)

            # following items have not been implemented yet
            # self.toolmenu.add_command(label="Upload new trackingserver", state=enabled)
            # self.toolmenu.add_command(label="Reboot device", state=enabled)

    # generic methods for the file and help menus
    @staticmethod
    def about():
        messagebox.showinfo("About", "Kinsei Configuration Editor v.1.0.0\n\nCopyright Xetal@2017")

    def new(self):
        if messagebox.askokcancel("New Configuration", "Any modification that has not been "
                                                       "saved will be lost, proceed?"):
            self.configEditor.delete(1.0, END)

    def open(self):
        if messagebox.askokcancel("New Configuration", "Any modification that has not been "
                                                       "saved will be lost, proceed?"):
            self.configEditor.delete(1.0, END)
            file = filedialog.askopenfile(parent=self.root, mode='rb', title='Select a file')
            if file is not None:
                for line in file.readlines():
                    line = line.decode('utf-8')
                    tag = 'command'
                    if line is not '':
                        line.strip()
                        if line[0] == '#':
                            tag = 'comment'
                        else:
                            if line.split('=')[0] not in parameters:
                                tag = 'syntaxerror'
                    self.configEditor.insert(END, line, tag)
                file.close()

    def save(self):
        file = filedialog.asksaveasfile(mode='w')
        if file is not None:
            # slice off the last character from get, as an extra return is added
            data = self.configEditor.get('1.0', END + '-1c')
            file.write(data)
            file.close()

    # noinspection PyUnusedLocal
    def exit(self, _notUSed=0):
        if messagebox.askokcancel("Quit", "Any modification that has not been "
                                          "saved will be lost, proceed?"):
            self.root.destroy()

    # methods for device tool execution
    def forceConnect(self):
        self.ssh.disconnect()
        state = self.ssh.connect(True)
        self.setDeviceTools(state)

    def forceDisconnect(self):
        self.ssh.disconnect(True)
        self.setDeviceTools(False)

    def readConfig(self):
        config = self.ssh.readConfiguration()
        if config is None:
            messagebox.showerror("Error", "Failed to read the configuration file of the device at " + self.ssh.hostname)
        else:
            self.new()
            for line in config:
                tag = 'command'
                if line is not '':
                    line.strip()
                    if line[0] == '#':
                        tag = 'comment'
                    else:
                        if line.split('=')[0] not in parameters:
                            tag = 'syntaxerror'
                self.configEditor.insert(END, line + '\n', tag)

    def sendConfig(self):
        config = self.configEditor.get(1.0, END)
        if not self.verify(False):
            test = self.ssh.writeConfiguration(config)
            if test is None:
                messagebox.showerror("Error", "Failed to send the configuration to device " + self.ssh.hostname)
                return False
            elif self.showMessage:
                messagebox.showinfo("Operation completed", "The configuration has been sent to device " +
                                    self.ssh.hostname)
                return True

    def stopService(self):
        if self.ssh.stopServer() is None:
            messagebox.showerror("Error", "Failed to stop the kinsei server of device " + self.ssh.hostname)
        elif self.showMessage:
            messagebox.showinfo("Operation completed", "The Kinser server of device " +
                                self.ssh.hostname + " has been stopped")

    def startService(self):
        if self.ssh.startServer() is None:
            messagebox.showerror("Error", "Failed to start the kinsei server of device " + self.ssh.hostname)
        elif self.showMessage:
            messagebox.showinfo("Operation completed", "The Kinser server of device " +
                                self.ssh.hostname + " has been started")

    def restartService(self):
        if self.platform < 2.1:
            self.ssh.killServer()
            if self.showMessage:
                messagebox.showinfo("Operation completed", "The Kinser server of device " +
                                    self.ssh.hostname + " will restart within 30 seconds")
        else:
            if self.ssh.restartServer() is None:
                messagebox.showerror("Error", "Failed to restart the kinsei server of device " + self.ssh.hostname)
            elif self.showMessage:
                messagebox.showinfo("Operation completed", "The Kinser server of device " +
                                    self.ssh.hostname + " has been restarted")

    def sendConfigRestart(self):
        if self.sendConfig():
            self.restartService()

    # check if there are value errors in the provided configuration line
    @staticmethod
    def checkForValueErrorInLine(confLineData):
        commandCheck = parameters[confLineData[0]]
        correct = True
        if commandCheck[0] == 'num':
            if confLineData[1].strip().lstrip('-').replace('.', '', 1).isdigit():
                value = float(confLineData[1].strip())
                if value < commandCheck[1]:
                    correct = False
                elif commandCheck[2] is not None:
                    if value > commandCheck[2]:
                        correct = False
            else:
                correct = False
        elif commandCheck[0] == 'bool':
            if (confLineData[1].strip() != '1') and (confLineData[1].strip() != '0'):
                correct = False
            pass
        elif commandCheck[0] == 'set':
            for angle in confLineData[1].strip():
                if angle not in commandCheck[1]:
                    correct = False
        return correct

    # used to check the code for consistency and syntax
    def verify(self, showOK=True):

        syntaxError = 0
        valueError = 0
        senError = {
            'position': False,
            'declared': 0,
            'present': 0,
            'angleposition': False
        }

        config = self.configEditor.get(1.0, END)
        pureConfig = [x for x in config.split('\n') if x is not ""]
        pureConfig = [x for x in pureConfig if x[0] != '#']

        for line in pureConfig:
            confLineData = line.split('=')
            # check for syntax errors
            if confLineData[0] not in parameters:
                syntaxError += 1
            else:
                # check for value errors
                if not self.checkForValueErrorInLine(confLineData):
                    valueError += 1
                if confLineData[0] == 'SEN':
                    if senError['declared'] == 0:
                        senError['position'] = True
                    senError['present'] += 1
                if confLineData[0] == 'NSENS':
                    if senError['present'] != 0:
                        senError['position'] = True
                    senError['declared'] = int(confLineData[1])
                if confLineData[0] == 'SENSORANGLE_NR':
                    if senError['present'] != 0:
                        senError['angleposition'] = True

        error = (syntaxError != 0) or (valueError != 0) or senError['position'] or senError['angleposition'] \
                or (senError['declared'] != senError['present'])

        if error:
            message = "The configuration file has errors:\n\n"
            if syntaxError > 0:
                message += "Syntax errors: " + str(syntaxError) + "\n"
            if valueError > 0:
                message += "Value errors: " + str(valueError) + "\n"
            if senError['present'] != senError['declared']:
                message += "Sensor error. Declared " + str(senError['declared']) + \
                           " while defined " + str(senError['present']) + "\n"
            if senError['position']:
                message += "\nNSENS command placed after SEN \n"
            if senError['angleposition']:
                message += "\nSENSORANGLE_NR command placed after SEN \n"
            messagebox.showerror("Configuration Error", message)
        else:
            if showOK and self.showMessage:
                messagebox.showinfo("Operation Completed", "The configuration file has no errors\n")
        return error


def start():
    root = Tk()
    configurator = Configurator()
    gui.LoginGUI(root, configurator)
    root.mainloop()


if __name__ == '__main__':
    start()
