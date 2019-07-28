#!/usr/bin/python
# script to write file stored default values due to power outage
#
######################################################################
## Application file name: powerout.py                               ##
## Description: A component of Ay-yahs-Greenhouse Automation System ##
## Description: Resets default values after power outage.           ##
## Description: 												                            ##
## Version: 1.04										                                ##
## Project Repository: https://git.io/fhhsY				                  ##
## Copyright (C) 2019 The Groundhog Whisperer				                ##
######################################################################
#
import os
import subprocess
import time


# Outputs status filename
OUTPUTS_STATUS_FILE_NAME = '/var/www/html/outputs.txt'

# Solenoid valve status filename
SOLENOID_STATUS_FILE_NAME = '/var/www/html/solenoid.txt'

# Set all output values to Off in case of power failure
CURRENT_OUTPUTS_STATUS_LIST = ["Off\n", "Off\n", "Off\n"]
#CURRENT_OUTPUTS_STATUS_LIST[0] = "Off\n"
#CURRENT_OUTPUTS_STATUS_LIST[1] = "Off\n"
#CURRENT_OUTPUTS_STATUS_LIST[2] = "Off\n"
outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'w')
outputs_status_file_handle.writelines(CURRENT_OUTPUTS_STATUS_LIST)
outputs_status_file_handle.close()

# Set the solenoid valve status to Closed in case of power failure
current_solenoid_valve_status = 'Closed'
solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
solenoid_status_file_handle.write(current_solenoid_valve_status)
solenoid_status_file_handle.close()

# Disable Output #1 opened using a pigpiod command if a power outage has occured
pigs_gpio_command_line = ["/usr/bin/pigs", "w 5 0"]
p = subprocess.Popen(pigs_gpio_command_line)

# Disable Output #2 opened using a pigpiod command if a power outage has occured
pigs_gpio_command_line = ["/usr/bin/pigs", "w 12 0"]
p = subprocess.Popen(pigs_gpio_command_line)

# Disable Output #3 opened using a pigpiod command if a power outage has occured
pigs_gpio_command_line = ["/usr/bin/pigs", "w 6 0"]
p = subprocess.Popen(pigs_gpio_command_line)

# Disable relay #3 opened using a pigpiod command if a power outage has occured
pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 0"]
p = subprocess.Popen(pigs_gpio_command_line)

