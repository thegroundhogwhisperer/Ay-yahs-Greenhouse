#!/usr/bin/python
# script to write file stored default values due to power outage

import os
import subprocess
import time


# outputs status filename
outputsStatusFilename = '/var/www/html/outputs.txt'

# solenoid valve status filename
solenoidStatusFilename = '/var/www/html/solenoid.txt'

# set all output values to Off in case of power failure
currentOutputStatusList = ["Off\n", "Off\n", "Off\n"]
#currentOutputStatusList[0] = "Off\n"
#currentOutputStatusList[1] = "Off\n"
#currentOutputStatusList[2] = "Off\n"
outputsStatusFileHandle = open(outputsStatusFilename, 'w')
outputsStatusFileHandle.writelines(currentOutputStatusList)
outputsStatusFileHandle.close()

# set the solenoid valve status to Closed in case of power failure
currentSolenoidValveStatus = 'Closed'
solenoidStatusFileHandle = open(solenoidStatusFilename, 'w')
solenoidStatusFileHandle.write(currentSolenoidValveStatus)
solenoidStatusFileHandle.close()

# disable Output #1 opened using a pigpiod command if a power outage has occured
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

# disable Output #2 opened using a pigpiod command if a power outage has occured
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 12 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

# disable Output #3 opened using a pigpiod command if a power outage has occured
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 6 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

# disable relay #3 opened using a pigpiod command if a power outage has occured
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

