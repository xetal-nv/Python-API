#!/usr/bin/python3

"""KinseiSSHCcient.py: client for SSH coontrol of a kinsei device"""

import paramiko
import time

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "july2017 or later"


class KinseiSSHclient(object):
    """ __init__:
    The costructor creates and opens SSH channel.

    Arguments are as follows:
    username:           username to login to the device
    password:           password to login to the device
    hostname:           device IP for SSH (assume standard port 22)
    offline:              True only when the app is to be used offline
    """

    def __init__(self, username, password, hostname='192.168.76.1', offline=False):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.config = None
        self.trace = None
        self.connected = False
        self.ssh = paramiko.SSHClient()
        if not offline:
            self.connect()

    """ __del__:
    Destructor
    """

    def __del__(self):
        self.disconnect()

    """sendCommand:
    Sends the command to the device via the SSH channel.
    When 'offline' is True, the answer is printed on console, ignore otherwise"""

    def sendCommand(self, command, offline=False):
        if self.ssh:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available and in debug mode
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata
                    if offline:
                        print(str(alldata, "utf8"))

    """connect:
    Reconnect to the channel associated with the object.
    When 'forced' is True, it ignores the current channel state"""

    def connect(self, forced=False):
        if (not self.connected) or forced:
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password)
                self.connected = True
            except:
                self.connected = False
                self.ssh = None
        return self.connected

    """ disconnect:
    Disconnect from the device without removing the object"""

    def disconnect(self, forced=False):
        if self.connected or forced:
            self.ssh.close()
            self.connected = False

    """ readFile:
    Read file filename (including path) from the device"""

    def readFile(self, filename):
        if self.connected:
            try:
                stdin, stdout, stderr = self.ssh.exec_command('cat TrackingServer/' + filename)
                self.config = str(stdout.read()).split('\\n')[0:-1]
                self.config[0] = self.config[0].lstrip('b\'')
                return self.config
            except:
                pass
        return None

    """ archiveFile:
    Make a '.archive' copy of file filename (including path) on the device"""

    def archiveFile(self, fullFileName):
        if self.connected:
            try:
                self.ssh.exec_command('rm ' + fullFileName + ".archive")
                stdin, stdout, stderr = self.ssh.exec_command('cp ' + fullFileName + ' ' + fullFileName + ".archive")
                self.config = str(stdout.read()).split('\\n')[0:-1]
                self.config[0] = self.config[0].lstrip('b\'')
                return self.config
            except:
                pass
        return None

    """ service:
    Manage the Kinsei server via the service interface. 
    Accepted actions are START, STOP, RESTART, RELOAD (confguration file).
    Shortcut methids are provided for readability (stopServer, startServer,
    restartServer, reloadServerConfiguration) """

    def service(self, command, delay=0):
        if self.connected:
            try:
                stdin, stdout, stderr = self.ssh.exec_command('/etc/init.d/xetal ' + command)
                returnValue = str(stdout.read()) == 'b\'\''
                # Delay used to account for service delay
                time.sleep(delay)
                return returnValue
            except:
                pass
        return None

    def stopServer(self):
        return self.service('stop')

    def startServer(self):
        return self.service('start', 3)

    def restartServer(self):
        return self.service('restart', 4)

    def killServer(self):
        if self.connected:
            try:
                self.sendCommand('killall TrackingServer')
                time.sleep(2)
                return True
            except:
                pass
        return None

    def reloadServerConfiguration(self):
        return self.service('reload', 2)

    """ readConfiguration:
    Read the kinsei server configuration file"""

    def readConfiguration(self):
        return self.readFile('TrackingServer.conf')

    """ writeConfiguration:
    Writes a new kinsei server configuration file.
    The previous file is archived"""

    def writeConfiguration(self, configuration):
        if self.connected:
            try:
                # self.archiveFile('/root/TrackingServer/TrackingServer.conf')
                self.archiveFile('TrackingServer/TrackingServer.conf')
                conf = configuration.split("\n")
                # self.sendCommand('rm /root/TrackingServer/TrackingServer.conf')
                self.sendCommand('rm TrackingServer/TrackingServer.conf')
                for line in conf:
                    # self.sendCommand('printf \'' + line + '\n\' >> ' + '/root/TrackingServer/TrackingServer.conf')
                    self.sendCommand('printf \'' + line + '\n\' >> ' + 'TrackingServer/TrackingServer.conf')
                return True
            except:
                pass
        return None

    """ readStoredTrace:
    Read the trace file, if it exists"""

    def readStoredTrace(self):
        return self.readFile('data.raw')
