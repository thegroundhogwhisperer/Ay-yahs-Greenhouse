# Ay-yahs-Greenhouse

# Python script for VOX activated radio frequency broadcast transmissions containing audible notifications of greenhouse environmental conditions on an Ubuntu 18 desktop 

# Warning: Laws governing the operation of a radio frequency transceiver or transmitter are clearly established and strictly enforced by federal regulations.

# Prerequisites

 Non-interactive network downloader (wget)

 Ubuntu speech-dispatcher (spd-say)

 Desktop notification application (notify-send)

 General-purpose software audio FSK modem (minimodem)

 Cross-platform command line audio manipulation utility (sox)

 Python 3

 Python classes for generating Slow-scan Television transmissions (PySSTV)

  sudo apt install python3-pip

  sudo python3 -m pip install PySSTV


# Produces:

 Desktop visual notification "bubble"

 Text-to-speech audio containing greenhouse environmental data

 RTTY audio output containing greenhouse environmental data

 SSTV audio output containing an image from the greenhouse interior


greenhousestatusttsrttysstvrf.py is a Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format and camera image data produced by /Greenhouse/camera.py and produces a desktop notification, text-to-speech audio output, RTTY data output, and SSTV data output. 

The audio output produced by greenhousestatusttsrttysstvrf.py can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse
environmental conditions. 

Before transmitting on any channel or frequency the channel should be monitored for at least 30 seconds to verify that the channel is clear/available. 

greenhousestatusttsrttysstvrf.py uses SoX to achieve verification of the current channels availability. SoX is used to record a 30 second sample of the current channel. SoX is then used to generate statistics from the audio recording to establish a maximum amplitude value. This maximum amplitude value is used to determine if the current broadcast should be deferred due to traffic on the channel or frequency. A maximum amplitude value > 0.025 is indicative of audio input/channel traffic. The maximum amplitude value may have to be adjusted relative other systems audio sample configurations.

