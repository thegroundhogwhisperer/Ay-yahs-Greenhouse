#!/usr/bin/env python
# encoding: utf-8

# greenhouse.py Version 1.02
# Copyright (C) 2019 The Groundhog Whisperer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This is a for-fun project created for the purpose of automating climate
# control and irrigation in a small greenhouse. Climate control and
# irrigation control is achieved by monitoring environmental sensor
# measurements. The environmental sensors measurements are then used to
# control a linear actuator, solenoid valve, small fan, and small heating
# pad. The information produced is displayed on a 16x2 LCD screen,
# broadcast via a wall message to the console, CSV file, and
# a SQLite database file.

# sqlite3 /var/www/html/greenhouse.db table creation command
# CREATE TABLE greenhouse(id INTEGER PRIMARY KEY AUTOINCREMENT, luminosity
# NUMERIC, temperature NUMERIC, humidity NUMERIC, soilmoisture NUMERIC,
# solenoidstatus TEXT, actuatorstatus TEXT, outputonestatus TEXT,
# outputtwostatus TEXT, outputthreestatus TEXT, currentdate DATE,
# currenttime TIME);

# Enable fake sensor input mode during execution
# Set this value to True if you would like to execute this
# script without any sensors (e.g. DHT22, LDR, soil moisture)
# and without a Pimoroni Automation hat.
ENABLE_FAKE_SENSOR_VALUES = True

# define the fake sensor values
FAKE_SOIL_MOISTURE_SENSOR_VALUE = 1.9
FAKE_LUMINOSITY_SENSOR_VALUE = 4.2
FAKE_HUMIDITY_SENSOR_VALUE = 50.01
FAKE_TEMPERATURE_SENSOR_VALUE = 72.28

# do not attempt to import the Adafruit_DHT module if fake sensor input mode is enabled
if ENABLE_FAKE_SENSOR_VALUES == False: import Adafruit_DHT

#import Adafruit_DHT
import datetime
import math
import time

# do not attempt to import the Pimoroni automationhat module if fake sensor input mode is enabled
if ENABLE_FAKE_SENSOR_VALUES == False: import automationhat

#import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import serial
import statistics
import subprocess
import sqlite3
import numpy as np
import matplotlib as plt
# plt initilized because it needs a different backend for the display
# to not crash when executed from the console
plt.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
#style.use('fivethirtyeight') # select the style of graph
from dateutil import parser


##################################################################
###################### Customizable Values #######################
##################################################################

# define the 16x2 RGB LCD device name connect via USB serial backpack kit
SERIAL_LCD_DEVICE_NAME = '/dev/ttyACM0'

# define the length of time in seconds to display each message on the LCD screen
DISPLAY_LCD_MESSAGE_LENGTH_SECONDS = .9

# messages broadcast via the wall command are suffixed with this string
WALL_TERMINAL_MESSAGE_SUFFIX_STRING = "Ay-yahs.Greenhouse.Garden.Area.One.Version.1.02"

# Switch to enable or disable LCD screen messages True/False
DISPLAY_LCD_SCREEN_MESSAGES_ACTIVE_SWTICH = False

# Switch to enable or disable broadcasting console wall messages True/False
DISPLAY_CONSOLE_WALL_MESSAGES_ACTIVE_SWTICH = False

# Enable verbose mode during execution
DISPLAY_PROCESS_MESSAGES = True

# define the model temperature sensor
# TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.AM2302
# TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.DHT11
#TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.DHT22

# do not attempt to define the temperature sensor modle if fake sensor input mode is enabled
if ENABLE_FAKE_SENSOR_VALUES == False: TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.DHT22

# define which GPIO data pin number the sensors DATA pin two is connected on
TEMPERATURE_SENSOR_GPIO = 25

# define the minimum and maximum humidity/temperature sensor values
# minimum humidity value
MIMIMUM_HUMIDITY_VALUE = 0

# maximum humidity value
MAXIMUM_HUMIDITY_VALUE = 100

# minimum temperature value
MINIMUM_TEMPERATURE_VALUE = -72

# maximum temperature value
MAXIMUM_TEMPERATURE_VALUE = 176

# Define the the minimum luminosity sensor value at 0.01VDC
MINIMUM_LUMINOSITY_SENSOR_VALUE = 0.01 

# Define the the soil moisture sensor value at 0.01VDC
MINIMUM_SOIL_MOISTURE_SENSOR_VALUE = 0.01

# sqlite database file name
SQLITE_DATABASE_FILE_NAME = '/var/www/html/greenhouse.db'

# comma separated value output local file name
INDEX_LOG_DATA_CSV_FILE_NAME = "/var/www/html/index.csv"

# comma separated value web/url file name
INDEX_LOG_DATA_CSV_URL_FILE_NAME = "index.csv"

# linear actuator status file name (Retracted | Extended
ACTUATOR_STATUS_FILE_NAME = '/home/pi/Greenhouse/actuator.txt'

# solenoid valve status file name (Open | Closed)
SOLENOID_STATUS_FILE_NAME = '/home/pi/Greenhouse/solenoid.txt'

# outputs status file name (On | Off)
OUTPUTS_STATUS_FILE_NAME = '/home/pi/Greenhouse/outputs.txt'

# linear actuator runtime value file name (seconds)
LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME = '/var/www/html/actuatorruntime.txt'

# minimum temperature sensor actuator retraction value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME = '/var/www/html/mintemactretract.txt'

# minimum temperature sensor output one off value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME = '/var/www/html/mintemoutoneoff.txt'

# minimum humidity sensor output one off value file name (percrent)
MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME = '/var/www/html/minhumoutoneoff.txt'

# minimum temperature sensor output two off value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME = '/var/www/html/mintemouttwooff.txt'

# minimum luminosity sensor output two off value file name (volts)
MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME = '/var/www/html/minlumouttwooff.txt'

# minimum soil moisture sensor open solenoid valve value file name (volts)
MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_OPEN_VALUE_FILE_NAME = '/var/www/html/minsoilsoleopen.txt'

# output two configuration between using temperature or luminosity value file name (Temperature | Luminosity)
OUTPUT_TWO_CONFIGURATION_BETWEEN_TEMPERATURE_OR_LUMINOSITY_VALUE_FILE_NAME = '/var/www/html/outtwotemlum.txt'

# luminosity graph image local output file name
GRAPH_IMAGE_LUMINOSITY_FILE_NAME = "/var/www/html/ghouselumi.png"

# temperature graph image local output file name
GRAPH_IMAGE_TEMPERATURE_FILE_NAME = "/var/www/html/ghousetemp.png"

# humidity graph image local output file name
GRAPH_IMAGE_HUMIDITY_FILE_NAME = "/var/www/html/ghousehumi.png"

# soil moisture graph image local output file name
GRAPH_IMAGE_SOIL_MOISTURE_FILE_NAME = "/var/www/html/ghousesoil.png"



##################################################################
#################### End Customizable Values #####################
##################################################################


##################################################################
################## Begin Subroutine Defintions ###################
##################################################################

# read control constant values from files on disk
def read_control_values_from_files():


	if DISPLAY_PROCESS_MESSAGES == True: print ("Reading control values from files on disk.")

	try: 
		global CURRENT_SOLENOID_VALVE_STATUS
		# read the current solenoid valve status
		solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'r')
		CURRENT_SOLENOID_VALVE_STATUS = solenoid_status_file_handle.readline()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read CURRENT_SOLENOID_VALVE_STATUS from file", CURRENT_SOLENOID_VALVE_STATUS)
		solenoid_status_file_handle.close()
	
	except OSError:
	
		print ("An error occurred reading file name: ", SOLENOID_STATUS_FILE_NAME)
		quit()

	try: 
		global CURRENT_ACTUATOR_EXTENSION_STATUS 
		# read the current linear actuator status
		actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'r')
		CURRENT_ACTUATOR_EXTENSION_STATUS = actuator_status_file_handle.readline()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read CURRENT_ACTUATOR_EXTENSION_STATUS from file", CURRENT_ACTUATOR_EXTENSION_STATUS)
		actuator_status_file_handle.close()
	
	except OSError:

		print ("An error occurred reading file name: ", ACTUATOR_STATUS_FILE_NAME)
		quit()

	try:
		global CURRENT_OUTPUT_STATUS_LIST
		# read the outputs status values
		outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'r')
		CURRENT_OUTPUT_STATUS_LIST = outputs_status_file_handle.readlines()
		outputs_status_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2] from file", CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2])
		# remove the \n new line char from the end of the line
		CURRENT_OUTPUT_STATUS_LIST[0] = CURRENT_OUTPUT_STATUS_LIST[0].strip('\n')
		CURRENT_OUTPUT_STATUS_LIST[1] = CURRENT_OUTPUT_STATUS_LIST[1].strip('\n')
		CURRENT_OUTPUT_STATUS_LIST[2] = CURRENT_OUTPUT_STATUS_LIST[2].strip('\n')
	
	except OSError:

		print ("An error occurred reading file name: ", OUTPUTS_STATUS_FILE_NAME)
		quit()

	try: 
		global LINEAR_ACTUATOR_RUN_TIME_VALUE
		# read the current linear actuator runtime value from a file
		actuator_runtime_value_file_handle = open(LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME, 'r')
		LINEAR_ACTUATOR_RUN_TIME_VALUE = actuator_runtime_value_file_handle.readline()
		actuator_runtime_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read LINEAR_ACTUATOR_RUN_TIME_VALUE from file", LINEAR_ACTUATOR_RUN_TIME_VALUE)
	
	except OSError:

		print ("An error occurred reading file name: ", LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME)
		quit()

	try: 

		global MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT
		# read the minimum temperature linear actuator retract value from a file
		minimum_temperature_acturator_retract_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT = minimum_temperature_acturator_retract_value_file_handle.readline()
		minimum_temperature_acturator_retract_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT from file", MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME)
		quit()


	try: 
		global MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF
		# read the minimum temperature sensor output one off value from a file
		minimum_temperature_sensor_output_one_off_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF = minimum_temperature_sensor_output_one_off_value_file_handle.readline()
		minimum_temperature_sensor_output_one_off_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF from file", MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF)
	
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		global MINIMUM_HUMIDITY_OUTPUT_ONE_OFF
		# read the minimum humidity sensor output one off value from a file
		minimum_humidity_sensor_output_one_off_value_file_handle = open(MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_HUMIDITY_OUTPUT_ONE_OFF = minimum_humidity_sensor_output_one_off_value_file_handle.readline()
		minimum_humidity_sensor_output_one_off_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read MINIMUM_HUMIDITY_OUTPUT_ONE_OFF from file", MINIMUM_HUMIDITY_OUTPUT_ONE_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		global MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF 
		# read the minimum temperature sensor output two on value from a file
		minimum_temperature_sensor_output_two_off_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF = minimum_temperature_sensor_output_two_off_value_file_handle.readline()
		minimum_temperature_sensor_output_two_off_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF from file", MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		global MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF
		# read the minimum luminosity sensor output two on value from a file
		minimum_luminosity_sensor_output_two_off_value_file_handle = open(MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF = minimum_luminosity_sensor_output_two_off_value_file_handle.readline()
		minimum_luminosity_sensor_output_two_off_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF from file", MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		global MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN
		# read the soil moisture sensor solenoid open value from a file
		minimum_soil_moisture_sensor_solenoid_open_value_file_handle = open(MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_OPEN_VALUE_FILE_NAME, 'r')
		MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN = minimum_soil_moisture_sensor_solenoid_open_value_file_handle.readline()
		minimum_soil_moisture_sensor_solenoid_open_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN from file", MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_OPEN_VALUE_FILE_NAME)
		quit()

	try: 
		global OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY
		# read the output two control configuration value switching between temperature or luminosity from a file
		output_two_configuration_value_file_handle = open(OUTPUT_TWO_CONFIGURATION_BETWEEN_TEMPERATURE_OR_LUMINOSITY_VALUE_FILE_NAME, 'r')
		OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY = output_two_configuration_value_file_handle.readline()
		output_two_configuration_value_file_handle.close()
		if DISPLAY_PROCESS_MESSAGES == True: print ("Read OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY from file", OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY)
		
	except OSError:

		print ("An error occurred reading file name: ", OUTPUT_TWO_CONFIGURATION_BETWEEN_TEMPERATURE_OR_LUMINOSITY_VALUE_FILE_NAME)
		quit()



# temperature and humidity value read input subroutine
def read_temperature_humidity_values():

	if DISPLAY_PROCESS_MESSAGES == True: print ("Reading temperature and humidity values")
	# the sensor may produce an erroneous reading greater or less than
	# the possible measuring range of the device
	# a for loop retrys the read process until values within the scope
	# of the possbile measuring range are obtained
	for i in range(0, 15):

		try:

			global current_temperature_sensor_value
			global current_humidity_sensor_value

			if ENABLE_FAKE_SENSOR_VALUES == True: current_humidity_sensor_value = FAKE_HUMIDITY_SENSOR_VALUE
			if ENABLE_FAKE_SENSOR_VALUES == True: current_temperature_sensor_value = FAKE_TEMPERATURE_SENSOR_VALUE
			if ENABLE_FAKE_SENSOR_VALUES == True: print ("Fake sensor values enabled. Returning current_humidity_sensor_value, current_temperature_sensor_value:", current_humidity_sensor_value, current_temperature_sensor_value)
			if ENABLE_FAKE_SENSOR_VALUES == True: return(current_humidity_sensor_value, current_temperature_sensor_value)

			# create an instance of the dht22 class
			# pass the GPIO data pin number connected to the signal line
			# (pin #25 is broken out on the Pimoroni Automation HAT)
			# read the temperature and humidity values
			current_humidity_sensor_value, current_temperature_sensor_value = Adafruit_DHT.read_retry(
				TEMPERATURE_SENSOR_MODEL, TEMPERATURE_SENSOR_GPIO)
	
			if DISPLAY_PROCESS_MESSAGES == True: print ("Reading humidity value:", current_humidity_sensor_value)
			if DISPLAY_PROCESS_MESSAGES == True: print ("Reading temperature value:", current_temperature_sensor_value)

			if (current_temperature_sensor_value is not None and
				current_humidity_sensor_value is not None
				 ):
				# convert from a string to a floating-point number to an interger
				int(float(current_temperature_sensor_value))
				# convert from celsius to fahrenheit
				current_temperature_sensor_value = (current_temperature_sensor_value * 1.8) + 32
				# reformat as two decimals
				current_temperature_sensor_value = float("{0:.2f}".format(current_temperature_sensor_value))
				# reformat as two decimals
				current_humidity_sensor_value = float("{0:.2f}".format(current_humidity_sensor_value))

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_humidity_sensor_value < MIMIMUM_HUMIDITY_VALUE:", current_humidity_sensor_value, MIMIMUM_HUMIDITY_VALUE)

			if (current_humidity_sensor_value < MIMIMUM_HUMIDITY_VALUE):
				print('DHT sensor error humidity value less than minimum humidity value = %.2f Attempting reread' % current_humidity_sensor_value)

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_humidity_sensor_value > MAXIMUM_HUMIDITY_VALUE:", current_humidity_sensor_value, MAXIMUM_HUMIDITY_VALUE)

			if (current_humidity_sensor_value > MAXIMUM_HUMIDITY_VALUE):
				print('DHT sensor error humidity value greater than = %.2f Attempting reread' % current_humidity_sensor_value)

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value < MINIMUM_TEMPERATURE_VALUE:", current_temperature_sensor_value, MINIMUM_TEMPERATURE_VALUE)

			if (current_temperature_sensor_value < MINIMUM_TEMPERATURE_VALUE):
				print('DHT sensor error temperature value less than minimum temperature value = %.2f Attempting reread' % current_humidity_sensor_value)

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value > MAXIMUM_TEMPERATURE_VALUE:", current_temperature_sensor_value, MAXIMUM_TEMPERATURE_VALUE)

			if (current_temperature_sensor_value > MAXIMUM_TEMPERATURE_VALUE):
				print('DHT sensor error temperature value greater than maximum temperature value = %.2f Attempting reread' % current_humidity_sensor_value)

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_humidity_sensor_value > MIMIMUM_HUMIDITY_VALUE and current_humidity_sensor_value < MAXIMUM_HUMIDITY_VALUE and current_temperature_sensor_value > MINIMUM_TEMPERATURE_VALUE and current_temperature_sensor_value < MAXIMUM_TEMPERATURE_VALUE")

			if (current_humidity_sensor_value > MIMIMUM_HUMIDITY_VALUE and current_humidity_sensor_value < MAXIMUM_HUMIDITY_VALUE and
				current_temperature_sensor_value > MINIMUM_TEMPERATURE_VALUE and current_temperature_sensor_value < MAXIMUM_TEMPERATURE_VALUE):

				if DISPLAY_PROCESS_MESSAGES == True: print ("Success! Returning current_humidity_sensor_value, current_temperature_sensor_value:",current_humidity_sensor_value, current_temperature_sensor_value)

				return(current_humidity_sensor_value, current_temperature_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print("DHT sensor read failed: ", e.args)


# enable and disable outputs subroutine
# output #1 = 0, #2 = 1, #3 = 2
def control_outputs(output_number, output_status):

	if DISPLAY_PROCESS_MESSAGES == True: print ("Read OUTPUTS_STATUS_FILE_NAME:", OUTPUTS_STATUS_FILE_NAME)

	outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'r')
	CURRENT_OUTPUT_STATUS_LIST = outputs_status_file_handle.readlines()
	outputs_status_file_handle.close()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Read CURRENT_OUTPUT_STATUS_LIST:", CURRENT_OUTPUT_STATUS_LIST)

	current_output_status = CURRENT_OUTPUT_STATUS_LIST[output_number]
	# remove the \n new line char from the end of the line
	CURRENT_OUTPUT_STATUS_LIST[output_number] = CURRENT_OUTPUT_STATUS_LIST[output_number].strip('\n')

	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing CURRENT_OUTPUT_STATUS_LIST[output_number] == output_status:", CURRENT_OUTPUT_STATUS_LIST[output_number], output_status)

	if (CURRENT_OUTPUT_STATUS_LIST[output_number] == output_status):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Output already in correct state. Returning:", current_output_status)

		return(current_output_status)

	else:

		if (output_status == 'On'):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Using pigs to enable the output")

			# toggle output on
			if (output_number == 0):
				pigs_gpio_command_line = ["/usr/bin/pigs", "w 5 1"]
				p = subprocess.Popen(pigs_gpio_command_line)

			elif (output_number == 1):
				pigs_gpio_command_line = ["/usr/bin/pigs", "w 12 1"]
				p = subprocess.Popen(pigs_gpio_command_line)

			elif (output_number == 2):
				pigs_gpio_command_line = ["/usr/bin/pigs", "w 6 1"]
				p = subprocess.Popen(pigs_gpio_command_line)

			current_output_status = 'On'
			CURRENT_OUTPUT_STATUS_LIST[output_number] = "On\n"
			# write the modified status to a text file
			outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'w')
			outputs_status_file_handle.writelines(CURRENT_OUTPUT_STATUS_LIST)
			outputs_status_file_handle.close()

			if DISPLAY_PROCESS_MESSAGES == True: print ("Wrote the output status to:", OUTPUTS_STATUS_FILE_NAME)
			if DISPLAY_PROCESS_MESSAGES == True: print ("Returning:", current_output_status)
			return(current_output_status)

		if (output_status == 'Off'):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Using pigs to disable the output")
			# toggle output off
			if (output_number == 0):
				pigs_gpio_command_line = ["/usr/bin/pigs", "w 5 0"]
				p = subprocess.Popen(pigs_gpio_command_line)

			elif (output_number == 1):
				pigs_gpio_command_line = ["/usr/bin/pigs", "w 12 0"]
				p = subprocess.Popen(pigs_gpio_command_line)

			elif (output_number == 2):
				pigs_gpio_command_line = ["/usr/bin/pigs", "w 6 0"]
				p = subprocess.Popen(pigs_gpio_command_line)

			current_output_status = 'Off'
			CURRENT_OUTPUT_STATUS_LIST[output_number] = "Off\n"
			# write the modified status to a text file
			outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'w')
			outputs_status_file_handle.writelines(CURRENT_OUTPUT_STATUS_LIST)
			outputs_status_file_handle.close()

			if DISPLAY_PROCESS_MESSAGES == True: print ("Wrote the output status to:", OUTPUTS_STATUS_FILE_NAME)
			if DISPLAY_PROCESS_MESSAGES == True: print ("Returning:", current_output_status)

			return(current_output_status)


# linear actuator extension and retraction subroutine
def linear_actuator_extension_retraction(actuator_extension_status):

	if DISPLAY_PROCESS_MESSAGES == True: print ("Reading ACTUATOR_STATUS_FILE_NAME:", ACTUATOR_STATUS_FILE_NAME)

	global CURRENT_ACTUATOR_EXTENSION_STATUS
	actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'r')
	CURRENT_ACTUATOR_EXTENSION_STATUS = actuator_status_file_handle.readline()
	actuator_status_file_handle.close()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Read CURRENT_ACTUATOR_EXTENSION_STATUS:", CURRENT_ACTUATOR_EXTENSION_STATUS)

	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing CURRENT_ACTUATOR_EXTENSION_STATUS == actuator_extension_status:", CURRENT_ACTUATOR_EXTENSION_STATUS, actuator_extension_status)

	if (CURRENT_ACTUATOR_EXTENSION_STATUS == actuator_extension_status):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Linear actuator already in correct state. Returning CURRENT_ACTUATOR_EXTENSION_STATUS:", CURRENT_ACTUATOR_EXTENSION_STATUS)

		return(CURRENT_ACTUATOR_EXTENSION_STATUS)

	else:

		if (actuator_extension_status == 'Extended'):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Extending the linear actuator now")

			# toggle relay #2 on to extend the linear actuator
			if ENABLE_FAKE_SENSOR_VALUES == False: automationhat.relay.one.toggle()
			time.sleep(float(LINEAR_ACTUATOR_RUN_TIME_VALUE))

			# toggle relay #2 off
			if ENABLE_FAKE_SENSOR_VALUES == False: automationhat.relay.one.toggle()
			CURRENT_ACTUATOR_EXTENSION_STATUS = 'Extended'

			if DISPLAY_PROCESS_MESSAGES == True: print ("Writing the linear actuator status to ACTUATOR_STATUS_FILE_NAME", ACTUATOR_STATUS_FILE_NAME)

			# write the modified status to a text file
			actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'w')
			actuator_status_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
			actuator_status_file_handle.close()

			if DISPLAY_PROCESS_MESSAGES == True: print ("Returning CURRENT_ACTUATOR_EXTENSION_STATUS", CURRENT_ACTUATOR_EXTENSION_STATUS)

			return(CURRENT_ACTUATOR_EXTENSION_STATUS)

		if (actuator_extension_status == 'Retracted'):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Retracting the linear actuator now")

			# toggle relay #1 on to retract the linear actuator
			# only call the automationhat module if fake sensor input is disabled = False
			if ENABLE_FAKE_SENSOR_VALUES == False: automationhat.relay.two.toggle()
			time.sleep(float(LINEAR_ACTUATOR_RUN_TIME_VALUE))

			if DISPLAY_PROCESS_MESSAGES == True: print ("Writing the linear actuator status to ACTUATOR_STATUS_FILE_NAME", ACTUATOR_STATUS_FILE_NAME)

			# toggle relay #1 off
			# only call the automationhat module if fake sensor input is disabled = False
			if ENABLE_FAKE_SENSOR_VALUES == False: automationhat.relay.two.toggle()
			CURRENT_ACTUATOR_EXTENSION_STATUS = 'Retracted'
			# write the modified status to a text file
			actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'w')
			actuator_status_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
			actuator_status_file_handle.close()

			if DISPLAY_PROCESS_MESSAGES == True: print ("Returning CURRENT_ACTUATOR_EXTENSION_STATUS", CURRENT_ACTUATOR_EXTENSION_STATUS)

			return(CURRENT_ACTUATOR_EXTENSION_STATUS)


# solenoid valve open and close subroutine
def solenoid_valve_operation(solenoid_valve_status):

	if DISPLAY_PROCESS_MESSAGES == True: print ("Opening:", SOLENOID_STATUS_FILE_NAME)
	solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'r')
	CURRENT_SOLENOID_VALVE_STATUS = solenoid_status_file_handle.readline()
	solenoid_status_file_handle.close()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing CURRENT_SOLENOID_VALVE_STATUS == Comparing CURRENT_SOLENOID_VALVE_STATUS:", CURRENT_SOLENOID_VALVE_STATUS, solenoid_valve_status)

	if (CURRENT_SOLENOID_VALVE_STATUS == solenoid_valve_status):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Solenoid already in correct state. Returning CURRENT_SOLENOID_VALVE_STATUS:", CURRENT_SOLENOID_VALVE_STATUS)

		return(CURRENT_SOLENOID_VALVE_STATUS)

	else:

		
		if (solenoid_valve_status == 'Open'):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Calling pigs to open the solenoid valve")

			# toggle relay #3 on to open the solenoid valve
			pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 1"]
			p = subprocess.Popen(pigs_gpio_command_line)
			CURRENT_SOLENOID_VALVE_STATUS = 'Open'

			if DISPLAY_PROCESS_MESSAGES == True: print ("Saving the solenoid valve value to:", SOLENOID_STATUS_FILE_NAME)
			# write the modified status to a text file
			solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
			solenoid_status_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
			solenoid_status_file_handle.close()
			return(CURRENT_SOLENOID_VALVE_STATUS)

		if (solenoid_valve_status == 'Closed'):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Calling pigs to close the solenoid valve")

			# toggle relay #3 off to close the solenoid valve
			pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 0"]
			p = subprocess.Popen(pigs_gpio_command_line)
			CURRENT_SOLENOID_VALVE_STATUS = 'Closed'

			if DISPLAY_PROCESS_MESSAGES == True: print ("Saving the solenoid valve value to:", SOLENOID_STATUS_FILE_NAME)
			# write the modified status to a text file
			solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
			solenoid_status_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
			solenoid_status_file_handle.close()
			return(CURRENT_SOLENOID_VALVE_STATUS)


# analog to digital converter #1 read soil moisture sensor value subroutine
def read_soil_moisture_sensor_value():

	global current_soil_moisture_sensor_value

	if ENABLE_FAKE_SENSOR_VALUES == True: current_soil_moisture_sensor_value = FAKE_SOIL_MOISTURE_SENSOR_VALUE
	if ENABLE_FAKE_SENSOR_VALUES == True: print ("Fake sensor values enabled. Returning current_soil_moisture_sensor_value:", current_soil_moisture_sensor_value)
	if ENABLE_FAKE_SENSOR_VALUES == True: return(current_soil_moisture_sensor_value)

	if DISPLAY_PROCESS_MESSAGES == True: print ("Attempting to read the soil moisture sensor")
	# the ADC may produce an erroneous moisture reading less than 0.05VDC
	# a for loop retrys the read process until a value > 0.05VDC is returned
	for i in range(0, 25):
		try:
			# initilized the counter variable
			read_counter = 0
			temporary_value = float()
			temporary_values_list = list()
			current_soil_moisture_sensor_value = float()
			standard_deviation_of_sensor_values = 0

			# loop through multiple data reads
			while read_counter < 2:
				# read the moisture value from analog to
				# digital converter #1
				temporary_value = automationhat.analog[0].read()
				# keep one of the values in case the read is
				# consistent
				good_temporary_value = temporary_value
				time.sleep(.9)

				# populate a list of values
				temporary_values_list.append(temporary_value)
				read_counter = read_counter + 1

			# if the standard deviation of the series of
			# readings is zero then the sensor produced
			# multiple consistent values and we should
			# consider the data reliable and take actions

			# return the standard deviation of the list of values
			standard_deviation_of_sensor_values = math.sqrt(
				statistics.pvariance(temporary_values_list))
 			# if there is no difference in the values
			# use the good_temporary_value they are all
			# the same
			if (standard_deviation_of_sensor_values == 0):
				current_soil_moisture_sensor_value = good_temporary_value

			elif (standard_deviation_of_sensor_values != 0):
				# if there is a difference set the value
				# to zero and try again for a consistent
				# data read
				current_soil_moisture_sensor_value = 0


			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_soil_moisture_sensor_value <= MINIMUM_SOIL_MOISTURE_SENSOR_VALUE", current_soil_moisture_sensor_value, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE)

			if (current_soil_moisture_sensor_value <= MINIMUM_SOIL_MOISTURE_SENSOR_VALUE):
				print('ADC error read soil moisture value less than 0.05VDC = %.2f Attempting reread' % current_soil_moisture_sensor_value)

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_soil_moisture_sensor_value > MINIMUM_SOIL_MOISTURE_SENSOR_VALUE", current_soil_moisture_sensor_value, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE)

			if (current_soil_moisture_sensor_value > MINIMUM_SOIL_MOISTURE_SENSOR_VALUE):

				if DISPLAY_PROCESS_MESSAGES == True: print ("Have a good value for current_soil_moisture_sensor_value returning: ", current_soil_moisture_sensor_value)

				return(current_soil_moisture_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print("ADC sensor read failed: ", e.args)



# analog to digital converter #2 read light dependent resistor value subroutine
def read_luminosity_sensor_value():

	global current_luminosity_sensor_value

	if ENABLE_FAKE_SENSOR_VALUES == True: current_luminosity_sensor_value = FAKE_LUMINOSITY_SENSOR_VALUE
	if ENABLE_FAKE_SENSOR_VALUES == True: print ("Fake sensor values enabled. Returning current_luminosity_sensor_value:", current_luminosity_sensor_value)
	if ENABLE_FAKE_SENSOR_VALUES == True: return(current_luminosity_sensor_value)
		
	# the ADC may produce an erroneous luminisoty reading less than 0.00VDC
	# a for loop retrys the read process until a value > 0.00VDC is returned
	for i in range(0, 25):
		try:

			if DISPLAY_PROCESS_MESSAGES == True: print ("Attempting to read the luminosity sensor")
			# initilized the counter variable
			read_counter = 0
			temporary_value = float()
			temporary_values_list = list()

			current_luminosity_sensor_value = float()
			standard_deviation_of_sensor_values = 0

			# loop through multiple data reads
			while read_counter < 2:
				# read the light value from analog to digital converter #2
				temporary_value = automationhat.analog[1].read()
				# keep one of the values in case the read is
				# consistent
				good_temporary_value = temporary_value
				time.sleep(.9)

				# populate a list of values
				temporary_values_list.append(temporary_value)
			read_counter = read_counter + 1

			# If the standard deviation of the series of
			# readings is zero then the sensor produced
			# multiple consistent values and we should
			# consider the data reliable and take actions
			# return the standard deviation of the list of values
			standard_deviation_of_sensor_values = math.sqrt(statistics.pvariance(temporary_values_list))

			# if there is no difference in the values
			# use the good_temporary_value they are all
			# the same
			if (standard_deviation_of_sensor_values == 0):
				current_luminosity_sensor_value = good_temporary_value

			elif (standard_deviation_of_sensor_values != 0):
				# if there is a difference set the value
				# to zero and try again for a consistent
				# data read
				current_luminosity_sensor_value = 0

			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_luminosity_sensor_value < MINIMUM_LUMINOSITY_SENSOR_VALUE", current_luminosity_sensor_value, MINIMUM_LUMINOSITY_SENSOR_VALUE)

			if (current_luminosity_sensor_value < MINIMUM_LUMINOSITY_SENSOR_VALUE):
				print('ADC error read LDR value less than 0.01VDC = %.3f Attempting reread' %
				current_luminosity_sensor_value)
	
			if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE", current_luminosity_sensor_value, MINIMUM_LUMINOSITY_SENSOR_VALUE)


			if (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE):
	
				if DISPLAY_PROCESS_MESSAGES == True: print ("Have a good value for current_luminosity_sensor_value returning: ", current_luminosity_sensor_value)

				return(current_luminosity_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print("ADC sensor read failed: ", e.args)


# write text data to the 16x2 LCD subroutine as a serial device subroutine
def write_lcd_messages(write_lcd_message_content):

	if DISPLAY_PROCESS_MESSAGES == True: print ("Writing the 16x2 LCD screen:", write_lcd_message_content)
	ser = serial.Serial(SERIAL_LCD_DEVICE_NAME, 9600, timeout=1)
	# enable auto scrolling
	ser.write("%c%c" % (0xfe, 0x51))
	time.sleep(.1)

	# clear the screen
	ser.write("%c%c" % (0xfe, 0x58))
	time.sleep(.1)

	# change the lcd back light color
	# ser.write("%c%c%c%c%c" % (0xfe, 0xd0, 0x0, 0x0, 0xff))
	# time.sleep(.5)
	# ser.write("%c%c%c%c%c" % (0xfe, 0xd0, 0xff, 0xff, 0xff))
	# time.sleep(.5)

	ser.write(write_lcd_message_content)
	if DISPLAY_PROCESS_MESSAGES == True: print ("LCD screen content active for:", DISPLAY_LCD_MESSAGE_LENGTH_SECONDS)
	time.sleep(DISPLAY_LCD_MESSAGE_LENGTH_SECONDS)
	ser.write("%c%c" % (0xfe, 0x58))


# send console broadcast messages via wall
def write_wall_messages(write_wall_message_content):

	if DISPLAY_PROCESS_MESSAGES == True: print ("Broadcasting terminal wall message:", write_wall_message_content)
	wall_message_text = '%s' % write_wall_message_content
	wall_message_text = wall_message_text + ' @' + WALL_TERMINAL_MESSAGE_SUFFIX_STRING
	# the wall applications -n no banner
	# option requires root thus sudo
	wall_message_command_line = ['sudo', 'wall', '-n', wall_message_text]

	# comment out the following line to disable console notifications
	p = subprocess.Popen(wall_message_command_line)


# write CSV output file subroutine
def write_csv_output_file(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST):

	# begin file append of CSV file to the web server root
	# "Luminosity","Temperature","Humidity","Moisture",
	# "Solenoid","Actuator","Output1","Output2","Output3","Epoch"

	if DISPLAY_PROCESS_MESSAGES == True: print ("Opening to append INDEX_LOG_DATA_CSV_FILE_NAME", INDEX_LOG_DATA_CSV_FILE_NAME)
	csv_file_handle = open(INDEX_LOG_DATA_CSV_FILE_NAME, "a")

	if DISPLAY_PROCESS_MESSAGES == True: print ("Writing: ", current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

	csv_file_handle.write('"')
	csv_file_handle.write(str(current_luminosity_sensor_value))
	csv_file_handle.write('",\"')

	csv_file_handle.write('')
	csv_file_handle.write(str(current_temperature_sensor_value))
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write(str(current_humidity_sensor_value))
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write(str(current_soil_moisture_sensor_value))
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write('%s' % CURRENT_OUTPUT_STATUS_LIST[0])
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write('%s' % CURRENT_OUTPUT_STATUS_LIST[1])
	csv_file_handle.write('","')

	csv_file_handle.write('')
	csv_file_handle.write('%s' % CURRENT_OUTPUT_STATUS_LIST[2])
	csv_file_handle.write('","')

	# second since the epoch
	csv_file_handle.write('')
	csv_file_handle.write('%s' % time.time())
	csv_file_handle.write('"' + '\n')
	csv_file_handle.write('')
	if DISPLAY_PROCESS_MESSAGES == True: print ("Closing the file")
	csv_file_handle.close


# write sqlite database subroutine
def write_database_output(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST):
	# begin file table data insert of row
	try:
		if DISPLAY_PROCESS_MESSAGES == True: print ("Attempting to access SQLITE_DATABASE_FILE_NAME", SQLITE_DATABASE_FILE_NAME)
		# establish a connection to the database
		connection_sqlite_database = sqlite3.connect(SQLITE_DATABASE_FILE_NAME)
		curs = connection_sqlite_database.cursor()

		if DISPLAY_PROCESS_MESSAGES == True: print ("Performing row INSERT INTO table: ", current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2])
		# insert data rows into the table
		curs.execute("INSERT INTO greenhouse (luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime) VALUES((?), (?), (?), (?), (?), (?), (?), (?), (?), date('now','localtime'), time('now','localtime'))",
					 (current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2]))
		# commit the changes
		connection_sqlite_database.commit()
		curs.close
		if DISPLAY_PROCESS_MESSAGES == True: print ("Closing the database connection")
		connection_sqlite_database.close()

	except sqlite3.IntegrityError as e:
		print('Sqlite Error: ', e.args[0]) # error output


# read sqlite database generate graphs subroutine
def read_database_output_graphs():
	# begin file append of CSV file to the web server root
	# read a sqlite database table and generate a graph

	try:
		if DISPLAY_PROCESS_MESSAGES == True: print ("Attempting to access SQLITE_DATABASE_FILE_NAME", SQLITE_DATABASE_FILE_NAME)
		# establish a connection to the database
		connection_sqlite_database = sqlite3.connect(SQLITE_DATABASE_FILE_NAME)
		curs = connection_sqlite_database.cursor()

		if DISPLAY_PROCESS_MESSAGES == True: print ("Attempting to execute query")
		# select data rows from the table
		curs.execute('SELECT luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime FROM greenhouse ORDER BY ROWID DESC LIMIT 720 ')

		data_row_fetched_all = curs.fetchall()
		date_values = []
		date_values_no_year = []
		values_luminosity = []
		values_temperature = []
		values_humidity = []
		values_soil_moisture = []

		for row in data_row_fetched_all:
			values_luminosity.append(row[0])
			values_temperature.append(row[1])
			values_humidity.append(row[2])
			values_soil_moisture.append(row[3])
			date_values.append(parser.parse(row[9]))
			tempString = row[9].split("-", 1)
			date_values_no_year.append(tempString[1])
		
		if DISPLAY_PROCESS_MESSAGES == True: print ("Query complete")
		if DISPLAY_PROCESS_MESSAGES == True: print ("Generating luminosity graph image file: ", GRAPH_IMAGE_LUMINOSITY_FILE_NAME)
		plt.figure(0)
		plt.plot(values_luminosity)
		plt.ylabel('Luminosity [0.01-5.00 Volts]')
		plt.xlabel('720 x two minute read intervals = Last 24 Hours')
		#plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_LUMINOSITY_FILE_NAME)

		if DISPLAY_PROCESS_MESSAGES == True: print ("Generating temperature graph image file: ", GRAPH_IMAGE_TEMPERATURE_FILE_NAME)
		plt.figure(1)
		plt.plot(values_temperature)
		plt.ylabel('Temperature [Degrees Fahrenheit] ')
		plt.xlabel('720 x two minute read intervals = Last 24 Hours')
		#plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_TEMPERATURE_FILE_NAME)

		if DISPLAY_PROCESS_MESSAGES == True: print ("Generating humidity graph image file: ", GRAPH_IMAGE_HUMIDITY_FILE_NAME)
		plt.figure(2)
		plt.plot(values_humidity)
		plt.ylabel('Humidity [0%-100%] ')
		plt.xlabel('720 x two minute read intervals = Last 24 Hours')
		#plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_HUMIDITY_FILE_NAME)

		if DISPLAY_PROCESS_MESSAGES == True: print ("Generating soil moisture graph image file: ", GRAPH_IMAGE_SOIL_MOISTURE_FILE_NAME)
		plt.figure(3)
		plt.plot(values_soil_moisture)
		plt.ylabel('Soil Moisture [0.01-5.00 Volts] ')
		plt.xlabel('720 x two minute read intervals = Last 24 Hours')
		#plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_SOIL_MOISTURE_FILE_NAME)

		# commit the changes
		connection_sqlite_database.commit()
		curs.close
		if DISPLAY_PROCESS_MESSAGES == True: print ("Closing the database connection")
		connection_sqlite_database.close()

	except sqlite3.IntegrityError as e:
		print('Sqlite Error: ', e.args[0]) # error output



# display the current environmental information on the 16x2 LCD screen
def display_lcd_screen_messages():

	if (DISPLAY_LCD_SCREEN_MESSAGES_ACTIVE_SWTICH is True):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Calling write_lcd_message_content() from within display_lcd_screen_messages()")
		# display the luminosity value on the LCD
		write_lcd_message_content = 'Luminosity: %s' % current_luminosity_sensor_value
		write_lcd_messages(write_lcd_message_content)

		# display the temperature value on the LCD
		write_lcd_message_content = 'Temp: %s' % current_temperature_sensor_value
		write_lcd_messages(write_lcd_message_content)

		# display the humidity value on the LCD
		write_lcd_message_content = 'Humidity: %s' % current_humidity_sensor_value
		write_lcd_messages(write_lcd_message_content)

		# display soil moisture sensor on the LCD
		write_lcd_message_content = 'Soil moisture: %s' % current_soil_moisture_sensor_value
		write_lcd_messages(write_lcd_message_content)

		# display the linear actuator status on the LCD
		write_lcd_message_content = 'Linear actuator: %s' % CURRENT_ACTUATOR_EXTENSION_STATUS
		write_lcd_messages(write_lcd_message_content)
	
		# display the solenoid value status on the LCD
		write_lcd_message_content = 'Solenoid: %s' % CURRENT_SOLENOID_VALVE_STATUS
		write_lcd_messages(write_lcd_message_content)

		# display the outputs status on the LCD
		write_lcd_message_content = 'Output #1 status: %s' % CURRENT_OUTPUT_STATUS_LIST[0]
		write_lcd_messages(write_lcd_message_content)
		write_lcd_message_content = 'Output #2 status: %s' % CURRENT_OUTPUT_STATUS_LIST[1]
		write_lcd_messages(write_lcd_message_content)
		write_lcd_message_content = 'Output #3 status: %s' % CURRENT_OUTPUT_STATUS_LIST[2]
		write_lcd_messages(write_lcd_message_content)

	else:
		print ("LCD screen messages disabled in greenhouse.py header: DISPLAY_LCD_SCREEN_MESSAGES_ACTIVE_SWTICH = ", DISPLAY_LCD_SCREEN_MESSAGES_ACTIVE_SWTICH)


# display the current environmental information in the console window via wall messages
def display_console_wall_messages():

	if (DISPLAY_CONSOLE_WALL_MESSAGES_ACTIVE_SWTICH is True):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Calling write_wall_message_content() from within display_console_wall_messages()")
		# display the luminosity value via a console broadcast message
		write_wall_message_content = 'Luminosity: %s' % current_luminosity_sensor_value
		write_wall_messages(write_wall_message_content)
		# display the temperature value via a console broadcast message
		write_wall_message_content = 'Temp: %s' % current_temperature_sensor_value
		write_wall_messages(write_wall_message_content)

		# display the humidity value via a console broadcast message
		write_wall_message_content = 'Humidity: %s' % current_humidity_sensor_value
		write_wall_messages(write_wall_message_content)

		# display the soil moisture value via a console broadcast message
		write_wall_message_content = 'Soil moisture: %s' % current_soil_moisture_sensor_value
		write_wall_messages(write_wall_message_content)

		# display the solenoid value status via a console broadcast message
		write_wall_message_content = 'Solenoid: %s' % CURRENT_SOLENOID_VALVE_STATUS
		write_wall_messages(write_wall_message_content)

		# display the linear actuator status via a console broadcast message
		write_wall_message_content = 'Linear actuator: %s' % CURRENT_ACTUATOR_EXTENSION_STATUS
		write_wall_messages(write_wall_message_content)

		# display the outputs status via a console broadcast message
		write_wall_message_content = 'Output #1 status: %s' % CURRENT_OUTPUT_STATUS_LIST[0]
		write_wall_messages(write_wall_message_content)
		write_wall_message_content = 'Output #2 status: %s' % CURRENT_OUTPUT_STATUS_LIST[1]
		write_wall_messages(write_wall_message_content)
		write_wall_message_content = 'Output #3 status: %s' % CURRENT_OUTPUT_STATUS_LIST[2]
		write_wall_messages(write_wall_message_content)

	else:
		print ("Console wall messages disabled in greenhouse.py header: DISPLAY_CONSOLE_WALL_MESSAGES_ACTIVE_SWTICH = ", DISPLAY_CONSOLE_WALL_MESSAGES_ACTIVE_SWTICH)


# begin the process reading evaluating environmental data and broadcasting messages
def read_values_display_messages():

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling read_control_values_from_files()")
	# call the read system control values from files on disk subroutine
	read_control_values_from_files()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling read_luminosity_sensor_value()")
	# call the read luminosity sensor value subroutine
	current_luminosity_sensor_value = read_luminosity_sensor_value()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling read_temperature_humidity_values()")
	# call the read temperature and humidity value subroutine
	current_humidity_sensor_value, current_temperature_sensor_value = read_temperature_humidity_values()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling read_soil_moisture_sensor_value()")
	# call the read soil moisture sensor value subroutine
	current_soil_moisture_sensor_value = read_soil_moisture_sensor_value()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling display_lcd_screen_messages()")
	# call the display notifications on the 16x2 LCD screen subroutine
	display_lcd_screen_messages()

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling display_console_wall_messages()")
	# call the display notifications in the console as wall messages subroutine
	display_console_wall_messages()


# begin the process of evaluating environmental conditions and
# respond accordingly
def evaluate_environmental_conditions_perform_automated_responses():

	# evaulate if we close or open the window
	if DISPLAY_PROCESS_MESSAGES == True: print ("Performing evaluate_environmental_conditions_perform_automated_responses() comparison process now")
	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value <= int(MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT) and CURRENT_SOLENOID_VALVE_STATUS == 'Closed':", current_temperature_sensor_value, int(MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT), CURRENT_SOLENOID_VALVE_STATUS)
	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value > int(MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT) and CURRENT_SOLENOID_VALVE_STATUS == 'Closed':", current_temperature_sensor_value, int(MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT), CURRENT_SOLENOID_VALVE_STATUS)

	if (current_temperature_sensor_value <= int(MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT) and
		CURRENT_SOLENOID_VALVE_STATUS == 'Closed'
		):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Closing the window now")

		# retract the linear actuator and close the window
		actuator_extension_status = 'Retracted'
		CURRENT_ACTUATOR_EXTENSION_STATUS = linear_actuator_extension_retraction(actuator_extension_status)
	

	elif (current_temperature_sensor_value > int(MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT) and
		CURRENT_SOLENOID_VALVE_STATUS == 'Closed'
		):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Opening the window now")
		# extend the linear actuator and open the window
		actuator_extension_status = 'Extended'
		CURRENT_ACTUATOR_EXTENSION_STATUS = linear_actuator_extension_retraction(actuator_extension_status)


	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value >= int(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF) or current_humidity_sensor_value >= int(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF) and CURRENT_SOLENOID_VALVE_STATUS == 'Closed':", current_temperature_sensor_value, int(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF), current_humidity_sensor_value, int(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF), CURRENT_SOLENOID_VALVE_STATUS) 
	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value < int(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF) or current_humidity_sensor_value < int(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF) and CURRENT_SOLENOID_VALVE_STATUS == 'Closed':", current_temperature_sensor_value, int(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF), current_humidity_sensor_value, int(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF), CURRENT_SOLENOID_VALVE_STATUS) 

	# evaulate if we need to enable output #1 turn on the fan
	if (current_temperature_sensor_value >= int(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF) and
		current_humidity_sensor_value >= int(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF) and
		CURRENT_SOLENOID_VALVE_STATUS == 'Closed'
		 ):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Enabling Output #1")
		# enable output one
		output_number = 0
		output_status = 'On'
		current_output_status = control_outputs(output_number, output_status)

	elif (current_temperature_sensor_value < int(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF) and
		current_humidity_sensor_value < int(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF)
		):


		if DISPLAY_PROCESS_MESSAGES == True: print ("Disabling Output #1")

		# disable output one
		output_number = 0
		output_status = 'Off'
		current_output_status = control_outputs(output_number, output_status)

	# evaluate if temperature controls output two
	if DISPLAY_PROCESS_MESSAGES == True: print ("Evaluate if temperature or luminosity controls output #2")
	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY == 'Temperature':", OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY)

	if (OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY.rstrip() == 'Temperature'):
	#if (OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY == 'Temperature'):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Evaluate output #2 turned on by temperature")
		if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value <= int(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF:", current_temperature_sensor_value, int(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF))
		if DISPLAY_PROCESS_MESSAGES == True: print ("Evaluate output #2 turn off by temperature")
		if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_temperature_sensor_value > int(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF:", current_temperature_sensor_value, int(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF))

		# evaulate if we need to enable output #2 turn on the USB heating pad
		if (int(current_temperature_sensor_value) <= int(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF)):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Enabling Output #2 by temperature")

			# enable output two
			output_number = 1
			output_status = 'On'
			current_output_status = control_outputs(output_number, output_status)

		# evaulate if we need to disable output #2 turn off the USB heating pad
		elif (int(current_temperature_sensor_value) > int(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF)):
			
			if DISPLAY_PROCESS_MESSAGES == True: print ("Disable Output #2 by temperature")

			# disable output two
			output_number = 1
			output_status = 'Off'
			current_output_status = control_outputs(output_number, output_status)

	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY == 'Luminosity':", OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY)

	# evaluate if luminosity controls output two
	if (OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY.rstrip() == 'Luminosity'):
		
		if DISPLAY_PROCESS_MESSAGES == True: print ("Evaluate output #2 turn on by luminosity")
		if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_luminosity_sensor_value <= float(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF:", current_luminosity_sensor_value, float(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF))
		if DISPLAY_PROCESS_MESSAGES == True: print ("Evaluate output #2 turn off by luminosity")
		if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_luminosity_sensor_value > float(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF:", current_luminosity_sensor_value, float(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF))

		# evaulate if we need to enable output #2 turn on the grow light
		if (current_luminosity_sensor_value <= float(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF)):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Enable Output #2 by luminosity")

			# enable output two
			output_number = 1
			output_status = 'On'
			current_output_status = control_outputs(output_number, output_status)


		# evaulate if we need to disable output #2 turn off the grow light
		elif (current_luminosity_sensor_value > float(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF)):

			if DISPLAY_PROCESS_MESSAGES == True: print ("Disable Output #2 by luminosity")

			# disable output two
			output_number = 1
			output_status = 'Off'
			current_output_status = control_outputs(output_number, output_status)

	if DISPLAY_PROCESS_MESSAGES == True: print ("Evaluate if the solenoid valve should be open or closed")
	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_soil_moisture_sensor_value >= float(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN", current_soil_moisture_sensor_value, float(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN))
	if DISPLAY_PROCESS_MESSAGES == True: print ("Comparing current_soil_moisture_sensor_value < float(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN", current_soil_moisture_sensor_value, float(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN))

	# evaluate if the solenoid valve should be open or closed
	if (current_soil_moisture_sensor_value >= float(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN)):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Disabling output #1 to conserve power for the solenoid valve")

		# disable output one
		output_number = 0
		output_status = 'Off'
		current_output_status = control_outputs(output_number, output_status)

		if DISPLAY_PROCESS_MESSAGES == True: print ("Opening the solenoid valve now")

		# enable relay three opening the solenoid valve
		solenoid_valve_status = 'Open'
		solenoid_valve_operation(solenoid_valve_status)


	elif (current_soil_moisture_sensor_value < float(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN)):

		if DISPLAY_PROCESS_MESSAGES == True: print ("Closing the solenoid valve now")

		# disable relay three closing the solenoid valve
		solenoid_valve_status = 'Closed'
		solenoid_valve_operation(solenoid_valve_status)


# begin Sqlite database, CSV file, and graph image updates
def perform_write_database_csv_graph_image_update_process():

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling write_database_output() writing: ", current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

	# call the write database table subroutine
	write_database_output(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value,
						CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling write_csv_output_file() writing: ", current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

	# call the write CSV output file subroutine
	write_csv_output_file(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value,
					CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

	if DISPLAY_PROCESS_MESSAGES == True: print ("Calling read_database_output_graphs()")

	# call the read database table data output graph files subroutine
	read_database_output_graphs()


##################################################################
################### End Subroutine Defintions ####################
##################################################################

##################################################################
### Begin value read, notification, evaluation, update process ###
##################################################################

# begin reading system control values, current sensor values, and
# display system status messages

if DISPLAY_PROCESS_MESSAGES == True: print ("Calling read_values_display_messages()")

read_values_display_messages()

# begin evaluating environmental conditions and performing
# automation responses and configured

if DISPLAY_PROCESS_MESSAGES == True: print ("Calling evaluate_environmental_conditions_perform_automated_responses()")

evaluate_environmental_conditions_perform_automated_responses()

# begin Sqlite database file, CSV file, and graph
# image file updates

if DISPLAY_PROCESS_MESSAGES == True: print ("Calling perform_write_database_csv_graph_image_update_process()")

perform_write_database_csv_graph_image_update_process()

##################################################################
### End value read, notification, evaluation, update process ###
##################################################################

