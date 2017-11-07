# Python Kinsei Client, Examples and Applications 
### Version: 4.2.4 (trunk - in development)
### Advised Kinsei firmware: July2017
### Supported python version: 3.x
### In case of further help please contact us at contact@xetal.eu

NOTE => PLEASE INSTALL ALL DEPENDENCIES WITH PIP INSTALL -R REQUIREMENTS.TXT AND ADD TK (TKINTER) MANUALLY FOLLOWING THE INSTRUCTIONS FOR YOUR OS

NOTE => PLEASE NOTE THAT TRUNK DEVELOPMENT MIGHT CONTAIN ADDITIONAL BUGS OR UNFINISHED CODE

NOTE => TRUNK DEVELOPMENT IS ON APPLICATION VIRTUALFENCING.PY, WHICH IS NEITHER BUG FREE NOR COMPLETED


## Introduction
This module provides the Python3 libraries/API for the standard use of a Kinsei system, examples illustrating their usage and applications that can be used either to optimize the device or as examples for more complex application requiring open/closed loop control.

## Kinsei Libraries/API
All Kinsei libraries (or API) can be found in the folder ‘libs’ together with various generic libraries used by the provided examples and applications. Every library is provided with inline documentation.

Currently the following libraries are provided:

KinseiClient.py :
This library is used to established a connection to a Kinsei device and extract information about its status, number of people detected, position of detected persons, temperature map of the observed space and so on. 

KinseiTuner.py : 
This library is used for real-time tuning of the device functionality aiming at optimizing the results coming from the above library

KinseiSSHCcient.py :
This library is used to access the device SSH commands. It is normally used for advanced non-real time and destructive configuration and its usage is advised only after consultation with a Kinsei specialist

## Kinsei documentation
A kinsei device can be controlled by means of a simple TCP protocol for most of its functions. Currently the provided TCP interfaces are described in the following documents in the folder ‘docs’:

kinsei.interface.txt:
Describes the TCP interface used in the library KinseiClient.py

kinsei.tuning.interface.txt:
Describes the TCP interface used in the library KinseiTuner.py

sample.conf
Is a standard configuration file to be used as sample and instructions for the command ordering, syntax and usage

## Kinsei examples
Several examples are provided in the folder ‘example’ and 'server' to illustrate how a kinsei system can be used and how to use its API. Most examples can be executed by starting the python script: examples.py.
Currently the following examples are provided (* is used to indicate if accessible via examples.py):
 
aggregator.py: server collecting cumulative data from a kinsei device

presencehttp.py*: http server providing the number of detected people via a web page

communication.py: basic script connecting to a kinsei device, checking its tuning variables and providing in console in real-time the number of detected people and their position.

hotspot_viewer.py: client that retrieves the data from the aggregator.py server and displaying a hotspot map

hotspotmap.py*: collects and cumulates position data form the device and generate a hotspot map in real time

thermalmap.py*: displays a thermal map in real time (color coded or actual values)

trackingFusionViewer.py*: graphically shows the tracking and fusion data in real time. Provides also the number of detected people

trackingViewer.py*: graphically shows the tracking data in real time. Provides also the number of detected people

## Kinsei Tuners
Tuners are scripts that can be used to optimize and tune a kinsei device. Furthermore, they show advanced features (such as real time tuning) that can be used to implement open and closed loop control systems for application requiring more precise data or working in unpredictable environments. 

These Tuners also allow operations that were previously only possible by means of a manual SSH connetion to the device.

Currently the following applications are provided and can be accessed by running the script deviceconfig.py in folder ‘examples’:

tuner.py: this script can be used to retrieve and set parameters that affect the behavior of the device in real time (e.g. maximum person speed, temperature thresholds and so on).

configurator.py: this script can be used to perform full device configuration including kinsei firmware upload, changing room topology, sensor topology, storing of measurement of data locally, etc. When run, load the configuration file for an example of all available parameters and an explanation of their use. Please note, that altering the configuration takes effect only after stopping/starting or restarting the device (via the application itself). 

## Interactive Applications
Interactive Applications are examples that are meant to show interactively the functionality of the kit. 
They can be found in the folder 'interactiveapps' and can be execute via the script examples.py:

drawByMoving.py: example of detecting a position to draw lines. It is the basic algorithm needed for defining
entry and exit zones by moving around as well as it has a fun factor to it. Some parameters can be modified via GUI
in order to alter the behavior: line thickness, maximum line length, sensor frame rate and number of frames for a 
position to be considered stable if it moved in a given radius

virtualfencing.py: (in development) it allows to define and monitor events using a combination of back and front end elements. It also incliudes the tracking and draw by movement examples, and it supports resizing of the application window.

## Known issues
All scripts have a GUI which is not optimal for 4K laptops due to their high DPI count.


