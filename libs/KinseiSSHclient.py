#!/usr/bin/python3

"""KinseiSSHCcient.py: client for SSH coontrol of a kinsei device"""

import paramiko, time

__author__ = "Francesco Pessolano"
__copyright__ = "Copyright 2017, Xetal nv"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Francesco Pessolano"
__email__ = "francesco@xetal.eu"
__status__ = "release"
__requiredfirmware__ = "july2017 or later"


OFFLINE = False

# the class implmeneting the kinsei client
class KinseiSSHclient(object):
    """ __init__:
    """

    def __init__(self, username, password, hostname='192.168.76.1'):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.config = None
        self.trace = None
        self.connected = False
        self.ssh = paramiko.SSHClient()
        if not OFFLINE:
            self.connect()

    """ __del__:
    """

    def __del__(self):
        self.disconnect()

    def sendCommand(self, command, debug=False):
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
                    if debug:
                        print(str(alldata, "utf8"))

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

    def disconnect(self, forced=False):
        if self.connected or forced:
            self.ssh.close()
            self.connected = False

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

    def service(self, comand, delay=0):
        if self.connected:
            try:
                stdin, stdout, stderr = self.ssh.exec_command('/etc/init.d/xetal ' + comand)
                returnValue = str(stdout.read()) == 'b\'\''
                # Delay used to account for service delay
                time.sleep(delay)
                return returnValue
            except:
                pass
        return None

    def readConfiguration(self):
        return self.readFile('TrackingServer.conf')

    def writeConfiguration(self, configuration):
        if self.connected:
            try:
                self.archiveFile('/root/TrackingServer/TrackingServer.conf')
                conf = configuration.split("\n")
                self.sendCommand('rm /root/TrackingServer/TrackingServer.conf')
                for line in conf:
                    self.sendCommand('printf \'' + line + '\n\' >> ' + '/root/TrackingServer/TrackingServer.conf')
                return True
            except:
                pass
        return None

    def readStoredTrace(self):
        return self.readFile('data.raw')

    def stopServer(self):
        return self.service('stop')

    def startServer(self):
        return self.service('start', 3)

    def restartServer(self):
        return self.service('restart', 4)

    def reloadServerConfiguration(self):
        return self.service('reload', 2)
