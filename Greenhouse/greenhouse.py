#!/usr/bin/env python
# encoding: utf-8

# greenhouse.py Version 1.01
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
# broadcast via a wall message to the console, written to an HTML file,
# CSV file, and SQLite database file.

# sqlite3 /var/www/html/greenhouse.db table creation command
# CREATE TABLE greenhouse(id INTEGER PRIMARY KEY AUTOINCREMENT, luminosity
#  NUMERIC, temperature NUMERIC, humidity NUMERIC, soilmoisture NUMERIC,
#  solenoidstatus TEXT, actuatorstatus TEXT, outputonestatus TEXT,
#  outputtwostatus TEXT, outputthreestatus TEXT, currentdate DATE,
#  currenttime TIME);

import Adafruit_DHT
import datetime
import math
import time
import automationhat
time.sleep(0.1)  # short pause after ads1015 class creation recommended
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
style.use('fivethirtyeight')  # select the style of graph
from dateutil import parser


##################################################################
###################### Customizable Values #######################
##################################################################

# define the 16x2 RGB LCD device name connect via USB serial backpack kit
SERIAL_LCD_DEVICE_NAME = '/dev/ttyACM0'

# define the length of time in seconds to display each message on the LCD screen
DISPLAY_LCD_MESSAGE_LENGTH_SECONDS = .9

# messages broadcast via the wall command are suffixed with this string
WALL_TERMINAL_MESSAGE_SUFFIX_STRING = "Ay-yahs.Greenhouse.Garden.Area.One"

# string dispalyed in the header of the html output
WEBPAGE_HEADER_VALUE = "Ay-yah's Greenhouse Automation System"

# Switch to enable or disable LCD screen messages True/False
DISPLAY_LCD_SCREEN_MESSAGES_ACTIVE_SWTICH = True

# Switch to enable or disable broadcasting console wall messages True/False
DISPLAY_CONSOLE_WALL_MESSAGES_ACTIVE_SWTICH = True

# define the model temperature sensor
# TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.AM2302
# TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.DHT11
TEMPERATURE_SENSOR_MODEL = Adafruit_DHT.DHT22

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

# sqlite database file name
SQLITE_DATABASE_FILE_NAME = '/var/www/html/greenhouse.db'

# static webpage file name
STATIC_WEBPAGE_FILE_NAME = "/var/www/html/index.html"

# comma separated value output local file name
INDEX_LOG_DATA_CSV_FILE_NAME = "/var/www/html/index.csv"

# comma separated value web/url file name
INDEX_LOG_DATA_CSV_URL_FILE_NAME = "index.csv"

# linear actuator status file name (Retracted | Extended
ACTUATOR_STATUS_FILE_NAME = '/var/www/html/actuator.txt'

# solenoid valve status file name (Open | Closed)
SOLENOID_STATUS_FILE_NAME = '/var/www/html/solenoid.txt'

# outputs status file name (On | Off)
OUTPUTS_STATUS_FILE_NAME = '/var/www/html/outputs.txt'

# linear actuator runtime value file name (seconds)
LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME = '/var/www/html/actuatorruntime.txt'

# minimum luminosity sensor acutator retraction value file name (volts)
MINIMUM_LUMINOSITY_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME = '/var/www/html/minlumactretract.txt'

# minimum temperature sensor actuator retraction value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME = '/var/www/html/mintemactretract.txt'

# minimum humidity sensor acturator retraction value file name (percent)
MINIMUM_HUMIDITY_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME = '/var/www/html/minhumactretract.txt'

# minimum luminosity sensor acutator extension value file name (volts)
MINIMUM_LUMINOSITY_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME = '/var/www/html/minlumactextend.txt'

# minimum temperature sensor acturator extension value file name (percent)
MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME = '/var/www/html/mintemactextend.txt'

# minimum humidity sensor acturator extension value file name (percent)
MINIMUM_HUMIDITY_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME = '/var/www/html/minhumactextend.txt'

# minimum temperature sensor output one on value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_ON_VALUE_FILE_NAME = '/var/www/html/mintemoutoneon.txt'

# minimum humidity sensor output one on value file name (percrent)
MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_ON_VALUE_FILE_NAME = '/var/www/html/minhumoutoneon.txt'

# minimum temperature sensor output one off value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME = '/var/www/html/mintemoutoneoff.txt'

# minimum humidity sensor output one off value file name (percrent)
MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME = '/var/www/html/minhumoutoneoff.txt'

# minimum temperature sensor output two on value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_ON_VALUE_FILE_NAME = '/var/www/html/mintemouttwoon.txt'

# minimum temperature sensor output two off value file name (degrees)
MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME = '/var/www/html/mintemouttwooff.txt'

# minimum luminosity sensor output two on value file name (volts)
MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_ON_VALUE_FILE_NAME = '/var/www/html/minlumouttwoon.txt'

# minimum luminosity sensor output two off value file name (volts)
MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME = '/var/www/html/minlumouttwooff.txt'

# minimum soil moisture sensor open solenoid valve value file name (volts)
MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_OPEN_VALUE_FILE_NAME = '/var/www/html/minsoilsoleopen.txt'

# minimum soil moisture sensor close solenoid valve value file name (volts)
MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_CLOSED_VALUE_FILE_NAME = '/var/www/html/minsoilsoleclosed.txt'

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

# luminosity graph image web/url file name
GRAPH_IMAGE_LUMINOSITY_URL_FILE_NAME = "/ghouselumi.png"

# temperature graph image web/url file name
GRAPH_IMAGE_TEMPERATURE_URL_FILE_NAME = "/ghousetemp.png"

# humidity graph image web/url file name
GRAPH_IMAGE_HUMIDITY_URL_FILE_NAME = "/ghousehumi.png"

# soil moisture graph image web/url file name
GRAPH_IMAGE_SOIL_MOISTURE_URL_FILE_NAME = "/ghousesoil.png"

##################################################################
#################### End Customizable Values #####################
##################################################################


##################################################################
################## Begin Subroutine Defintions ###################
##################################################################

# read control constant values from files on disk
def read_control_values_from_files():

	try: 
		# read the current solenoid valve status
		solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'r')
		CURRENT_SOLENOID_VALVE_STATUS = solenoid_status_file_handle.readline()
		solenoid_status_file_handle.close()
	
	except OSError:
	
		print ("An error occurred reading file name: ", SOLENOID_STATUS_FILE_NAME)
		quit()

	try: 
		# read the current linear actuator status
		actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'r')
		CURRENT_ACTUATOR_EXTENSION_STATUS = actuator_status_file_handle.readline()
		actuator_status_file_handle.close()
	
	except OSError:

		print ("An error occurred reading file name: ", ACTUATOR_STATUS_FILE_NAME)
		quit()

	try: 
		# read the outputs status values
		outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'r')
		CURRENT_OUTPUT_STATUS_LIST = outputs_status_file_handle.readlines()
		outputs_status_file_handle.close()
		# remove the \n new line char from the end of the line
		CURRENT_OUTPUT_STATUS_LIST[0] = CURRENT_OUTPUT_STATUS_LIST[0].strip('\n')
		CURRENT_OUTPUT_STATUS_LIST[1] = CURRENT_OUTPUT_STATUS_LIST[1].strip('\n')
		CURRENT_OUTPUT_STATUS_LIST[2] = CURRENT_OUTPUT_STATUS_LIST[2].strip('\n')
	
	except OSError:

		print ("An error occurred reading file name: ", OUTPUTS_STATUS_FILE_NAME)
		quit()

	try: 
		# read the current linear actuator runtime value from a file
		actuator_runtime_value_file_handle = open(LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME, 'r')
		LINEAR_ACTUATOR_RUN_TIME = actuator_runtime_value_file_handle.readline()
		actuator_runtime_value_file_handle.close()
		print ("Current linear actuator runtime value read from a file: ", LINEAR_ACTUATOR_RUN_TIME_VALUE)
	
	except OSError:

		print ("An error occurred reading file name: ", LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum luminosity linear actuator retract value from a file
		minimum_luminosity_actuator_retract_value_file_handle = open(MINIMUM_LUMINOSITY_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME, 'r')
		MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT = minimum_luminosity_actuator_retract_value_file_handle.readline()
		minimum_luminosity_actuator_retract_value_file_handle.close()
		print ("Current minimum luminosity linear actuator retract value read from a file: ", MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_LUMINOSITY_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum temperature linear actuator retract value from a file
		minimum_temperature_acturator_retract_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT = minimum_temperature_acturator_retract_value_file_handle.readline()
		minimum_temperature_acturator_retract_value_file_handle.close()
		print ("Current minimum temperature linear actuator retract value read from a file: ", MINIMUM_TEMPERATURE_SENSOR_VALUE_ACTUATOR_RETRACT)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum humidity linear actuator retract value from a file
		minimum_humidity_actuator_retract_value_file_handle = open(MINIMUM_HUMIDITY_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME, 'r')
		MINIMUM_HUMIDITY_SENSOR_VALUE_ACTUATOR_RETRACT = minimum_humidity_actuator_retract_value_file_handle.readline()
		minimum_humidity_actuator_retract_value_file_handle.close()
		print ("Current minimum temperature linear actuator retract value read from a file: ", MINIMUM_HUMIDITY_SENSOR_VALUE_ACTUATOR_RETRACT)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_HUMIDITY_SENSOR_ACTUATOR_RETRACT_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum luminosity linear actuator retract value from a file
		minimum_luminosity_actuator_retract_value_file_handle = open(MINIMUM_LUMINOSITY_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME, 'r')
		MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND = minimum_luminosity_actuator_retract_value_file_handle.readline()
		minimum_luminosity_actuator_retract_value_file_handle.close()
		print ("Current minimum luminosity linear actuator extend value read from a file: ", MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_LUMINOSITY_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum temperature linear actuator extend value from a file
		minimum_temperature_actuator_extend_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_ACTUATOR_EXTEND = minimum_temperature_actuator_extend_value_file_handle.readline()
		minimum_temperature_actuator_extend_value_file_handle.close()
		print ("Current minimum temperature linear actuator extend value read from a file: ", MINIMUM_TEMPERATURE_ACTUATOR_EXTEND)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum humidity linear actuator extend value from a file
		minimum_humidity_actuator_extend_value_file_handle = open(MINIMUM_HUMIDITY_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME, 'r')
		MINIMUM_HUMIDITY_ACTUATOR_EXTEND = minimum_humidity_actuator_extend_value_file_handle.readline()
		minimum_humidity_actuator_extend_value_file_handle.close()
		print ("Current minimum humidity linear actuator extend value read from a file: ", MINIMUM_HUMIDITY_ACTUATOR_EXTEND)
	
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_HUMIDITY_SENSOR_ACTUATOR_EXTEND_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum temperature sensor output one on value from a file
		minimum_temperature_sensor_output_one_on_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_ON_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_OUTPUT_ONE_ON = minimum_temperature_sensor_output_one_on_value_file_handle.readline()
		minimum_temperature_sensor_output_one_on_value_file_handle.close()
		print ("Current minimum humidity output one on value read from a file: ", MINIMUM_TEMPERATURE_OUTPUT_ONE_ON)
	
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_ON_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum humidity sensor output one on value from a file
		minimum_humidity_sensor_output_one_on_value_file_handle = open(MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_ON_VALUE_FILE_NAME, 'r')
		MINIMUM_HUMIDITY_OUTPUT_ONE_ON = minimum_humidity_sensor_output_one_on_value_file_handle.readline()
		minimum_humidity_sensor_output_one_on_value_file_handle.close()
		print ("Current minimum humidity output one on value read from a file: ", MINIMUM_HUMIDITY_OUTPUT_ONE_ON)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_ON_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum temperature sensor output one off value from a file
		minimum_temperature_sensor_output_one_off_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF = minimum_temperature_sensor_output_one_on_value_file_handle.readline()
		minimum_temperature_sensor_output_one_off_value_file_handle.close()
		print ("Current minimum temperature output one off value read from a file: ", MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum humidity sensor output one off value from a file
		minimum_humidity_sensor_output_one_off_value_file_handle = open(MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_HUMIDITY_OUTPUT_ONE_OFF = minimum_humidity_sensor_output_one_off_value_file_handle.readline()
		minimum_humidity_sensor_output_one_off_value_file_handle.close()
		print ("Current minimum humidity output one off value read from a file: ", MINIMUM_HUMIDITY_OUTPUT_ONE_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_HUMIDITY_SENSOR_OUTPUT_ONE_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum temperature sensor output two on value from a file
		minimum_temperature_sensor_output_two_on_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_ON_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_OUTPUT_TWO_ON = minimum_temperature_sensor_output_two_on_value_file_handle.readline()
		minimum_temperature_sensor_output_two_on_value_file_handle.close()
		print ("Current minimum temperature output two on value read from a file: ", MINIMUM_TEMPERATURE_OUTPUT_TWO_ON)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_ON_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum temperature sensor output two off value from a file
		minimum_temperature_sensor_output_two_off_value_file_handle = open(MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF = minimum_temperature_sensor_output_two_off_value_file_handle.readline()
		minimum_temperature_sensor_output_two_off_value_file_handle.close()
		print ("Current minimum temperature output two off value read from a file: ", MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_TEMPERATURE_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum luminosity sensor output two on value from a file
		minimum_luminosity_sensor_output_two_on_value_file_handle = open(MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_ON_VALUE_FILE_NAME, 'r')
		MINIMUM_LUMINOSITY_OUTPUT_TWO_ON = minimum_luminosity_sensor_output_two_on_value_file_handle.readline()
		minimum_luminosity_sensor_output_two_on_value_file_handle.close()
		print ("Current minimum luminosity output two on value read from a file: ", MINIMUM_LUMINOSITY_OUTPUT_TWO_ON)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_ON_VALUE_FILE_NAME)
		quit()

	try: 
		# read the minimum luminosity sensor output two off value from a file
		minimum_luminosity_sensor_output_two_off_value_file_handle = open(MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME, 'r')
		MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF = minimum_luminosity_sensor_output_two_off_value_file_handle.readline()
		minimum_luminosity_sensor_output_two_off_value_file_handle.close()
		print ("Current minimum luminosity output two off value read from a file: ", MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_LUMINOSITY_SENSOR_OUTPUT_TWO_OFF_VALUE_FILE_NAME)
		quit()

	try: 
		# read the soil moisture sensor solenoid open value from a file
		minimum_soil_moisture_sensor_solenoid_open_value_file_handle = open(MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_OPEN_VALUE_FILE_NAME, 'r')
		MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN = minimum_soil_moisture_sensor_solenoid_open_value_file_handle.readline()
		minimum_soil_moisture_sensor_solenoid_open_value_file_handle.close()
		print ("Current minimum soil moisture sensor solenoid open value read from a file: ", MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_OPEN_VALUE_FILE_NAME)
		quit()

	try: 
		# read the soil moisture sensor solenoid close value from a file
		minimum_soil_moisture_sensor_solenoid_close_value_file_handle = open(MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_CLOSED_VALUE_FILE_NAME, 'r')
		MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN = minimum_soil_moisture_sensor_solenoid_close_value_file_handle.readline()
		minimum_soil_moisture_sensor_solenoid_close_value_file_handle.close()
		print ("Current minimum soil moisture sensor solenoid close value read from a file: ", MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED)
		
	except OSError:

		print ("An error occurred reading file name: ", MINIMUM_SOIL_MOISTURE_SENSOR_SOLENOID_VALVE_CLOSED_VALUE_FILE_NAME)
		quit()

	try: 
		# read the output two control configuration value switching between temperature or luminosity from a file
		output_two_configuration_value_file_handle = open(OUTPUT_TWO_CONFIGURATION_BETWEEN_TEMPERATURE_OR_LUMINOSITY_VALUE_FILE_NAME, 'r')
		OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY = output_two_configuration_value_file_handle.readline()
		output_two_configuration_value_file_handle.close()
		print ("Current output two configuration value between temperature or luminosity read from a file: ", OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY)
		
	except OSError:

		print ("An error occurred reading file name: ", OUTPUT_TWO_CONFIGURATION_BETWEEN_TEMPERATURE_OR_LUMINOSITY_VALUE_FILE_NAME)
		quit()



# temperature and humidity value read input subroutine
def read_temperature_humidity_values():

	# the sensor may produce an erroneous reading greater or less than
	# the possible measuring range of the device
	# a for loop retrys the read process until values within the scope
	# of the possbile measuring range are obtained
	for i in range(0, 15):
		try:

			# create an instance of the dht22 class
			# pass the GPIO data pin number connected to the signal line
			# (pin #25 is broken out on the Pimoroni Automation HAT)
			# read the temperature and humidity values
			current_humidity_sensor_value, current_temperature_sensor_value = Adafruit_DHT.read_retry(
				TEMPERATURE_SENSOR_MODEL, TEMPERATURE_SENSOR_GPIO)
	
			print(current_humidity_sensor_value)
			print(current_temperature_sensor_value)

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

			if (current_humidity_sensor_value < MIMIMUM_HUMIDITY_VALUE):
				print('DHT sensor error humidity value less than minimum humidity value = %.2f Attempting reread' % current_humidity_sensor_value)

			if (current_humidity_sensor_value > MAXIMUM_HUMIDITY_VALUE):
				print('DHT sensor error humidity value greater than  = %.2f Attempting reread' % current_humidity_sensor_value)

			if (current_temperature_sensor_value < MINIMUM_TEMPERATURE_VALUE):
				print('DHT sensor error temperature value less than minimum temperature value = %.2f Attempting reread' % current_humidity_sensor_value)

			if (current_temperature_sensor_value > MAXIMUM_TEMPERATURE_VALUE):
				print('DHT sensor error temperature value greater than maximum temperature value = %.2f Attempting reread' % current_humidity_sensor_value)

			if (current_humidity_sensor_value > MIMIMUM_HUMIDITY_VALUE and current_humidity_sensor_value < MAXIMUM_HUMIDITY_VALUE and
				current_temperature_sensor_value > MINIMUM_TEMPERATURE_VALUE and current_temperature_sensor_value < MAXIMUM_TEMPERATURE_VALUE):
				return(current_humidity_sensor_value, current_temperature_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print("DHT sensor read failed: ", e.args)


# enable and disable outputs subroutine
# output #1 = 0, #2 = 1, #3 = 2
def control_outputs(output_number, output_status):

	outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'r')
	CURRENT_OUTPUT_STATUS_LIST = outputs_status_file_handle.readlines()
	outputs_status_file_handle.close()
	current_output_status = CURRENT_OUTPUT_STATUS_LIST[output_number]
	# remove the \n new line char from the end of the line
	CURRENT_OUTPUT_STATUS_LIST[output_number] = CURRENT_OUTPUT_STATUS_LIST[output_number].strip('\n')

	if (CURRENT_OUTPUT_STATUS_LIST[output_number] == output_status):
		return(current_output_status)

	else:

		if (output_status == 'On'):
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
			return(current_output_status)

		if (output_status == 'Off'):
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
			return(current_output_status)


# linear actuator extension and retraction subroutine
def linear_actuator_extension_retraction(actuator_extension_status):

	actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'r')
	CURRENT_ACTUATOR_EXTENSION_STATUS = actuator_status_file_handle.readline()
	actuator_status_file_handle.close()

	if (CURRENT_ACTUATOR_EXTENSION_STATUS == actuator_extension_status):
		return(CURRENT_ACTUATOR_EXTENSION_STATUS)

	else:

		if (actuator_extension_status == 'Extended'):
			# toggle relay #2 on to extend the linear actuator
			automationhat.relay.one.toggle()
			time.sleep(LINEAR_ACTUATOR_RUN_TIME)

			# toggle relay #2 off
			automationhat.relay.one.toggle()
			CURRENT_ACTUATOR_EXTENSION_STATUS = 'Extended'

			# write the modified status to a text file
			actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'w')
			actuator_status_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
			actuator_status_file_handle.close()
			return(CURRENT_ACTUATOR_EXTENSION_STATUS)

		if (actuator_extension_status == 'Retracted'):

			# toggle relay #1 on to retract the linear actuator
			automationhat.relay.two.toggle()
			time.sleep(LINEAR_ACTUATOR_RUN_TIME)

			# toggle relay #1 off
			automationhat.relay.two.toggle()
			CURRENT_ACTUATOR_EXTENSION_STATUS = 'Retracted'
			# write the modified status to a text file
			actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'w')
			actuator_status_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
			actuator_status_file_handle.close()
			return(CURRENT_ACTUATOR_EXTENSION_STATUS)


# solenoid valve open and close subroutine
def solenoid_valve_operation(solenoid_valve_status):

	solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'r')
	CURRENT_SOLENOID_VALVE_STATUS = solenoid_status_file_handle.readline()
	solenoid_status_file_handle.close()

	if (CURRENT_SOLENOID_VALVE_STATUS == solenoid_valve_status):
		return(CURRENT_SOLENOID_VALVE_STATUS)

	else:

		if (solenoid_valve_status == 'Open'):
			# toggle relay #3 on to open the solenoid valve
			pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 1"]
			p = subprocess.Popen(pigs_gpio_command_line)
			CURRENT_SOLENOID_VALVE_STATUS = 'Open'

			# write the modified status to a text file
			solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
			solenoid_status_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
			solenoid_status_file_handle.close()
			return(CURRENT_SOLENOID_VALVE_STATUS)

		if (solenoid_valve_status == 'Closed'):
			# toggle relay #3 off to close the solenoid valve
			pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 0"]
			p = subprocess.Popen(pigs_gpio_command_line)
			CURRENT_SOLENOID_VALVE_STATUS = 'Closed'
			# write the modified status to a text file
			solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
			solenoid_status_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
			solenoid_status_file_handle.close()
			return(CURRENT_SOLENOID_VALVE_STATUS)


# analog to digital converter #1 read soil moisture sensor value subroutine
def read_soil_moisture_sensor_value():

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

			if (current_soil_moisture_sensor_value <= .09):
				print('ADC error read soil moisture value less than 0.05VDC = %.2f Attempting reread' % current_soil_moisture_sensor_value)

			if (current_soil_moisture_sensor_value > MINIMUM_SOIL_MOISTURE_SENSOR_VALUE):
				return(current_soil_moisture_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print("ADC sensor read failed: ", e.args)


# analog to digital converter #2 read light dependent resistor value subroutine
def read_luminosity_sensor_value():

	# the ADC may produce an erroneous luminisoty reading less than 0.00VDC
	# a for loop retrys the read process until a value > 0.00VDC is returned
	for i in range(0, 25):
		try:
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
			standard_deviation_of_sensor_values = math.sqrt(
				statistics.pvariance(temporary_values_list))

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

			if (current_luminosity_sensor_value < 0.05):
				print('ADC error read LDR value less than 0.01VDC = %.3f Attempting reread' % current_luminosity_sensor_value)

			if (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE):
				return(current_luminosity_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print("ADC sensor read failed: ", e.args)


# write text data to the 16x2 LCD subroutine as a serial device subroutine
def write_lcd_messages(write_lcd_message_content):

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
	time.sleep(DISPLAY_LCD_MESSAGE_LENGTH_SECONDS)
	ser.write("%c%c" % (0xfe, 0x58))


# send console broadcast messages via wall
def write_wall_messages(write_wall_message_content):

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

	csv_file_handle = open(INDEX_LOG_DATA_CSV_FILE_NAME, "a")

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
	csv_file_handle.close


# write sqlite database subroutine
def write_database_output(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST):
	# begin file table data insert of row
	try:
		# establish a connection to the database
		connection_sqlite_database = sqlite3.connect(SQLITE_DATABASE_FILE_NAME)
		curs = connection_sqlite_database.cursor()

		# insert data rows into the table
		curs.execute("INSERT INTO greenhouse (luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime) VALUES((?), (?), (?), (?), (?), (?), (?), (?), (?), date('now'), time('now'))",
					 (current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value,  CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2]))
		# commit the changes
		connection_sqlite_database.commit()
		curs.close
		connection_sqlite_database.close()

	except sqlite3.IntegrityError as e:
		print('Sqlite Error: ', e.args[0])  # error output


# read sqlite database generate graphs subroutine
def read_database_output_graphs():
	# begin file append of CSV file to the web server root
	# read a sqlite database table and generate a graph

	try:
		# establish a connection to the database
		connection_sqlite_database = sqlite3.connect(SQLITE_DATABASE_FILE_NAME)
		curs = connection_sqlite_database.cursor()

		# select data rows from the table
		curs.execute('SELECT luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime FROM greenhouse ORDER BY ROWID DESC LIMIT 1000 ')

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

		plt.figure(0)
		plt.plot(date_values_no_year, values_luminosity, '-')

		plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_LUMINOSITY_FILE_NAME)

		plt.figure(1)
		plt.plot(date_values_no_year, values_temperature, '-')
		plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_TEMPERATURE_FILE_NAME)

		plt.figure(2)
		plt.plot(date_values_no_year, values_humidity, '-')
		plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_HUMIDITY_FILE_NAME)

		plt.figure(3)
		plt.plot(date_values_no_year, values_soil_moisture, '-')
		plt.show(block=True)
		plt.savefig(GRAPH_IMAGE_SOIL_MOISTURE_FILE_NAME)

		# commit the changes
		connection_sqlite_database.commit()
		curs.close
		connection_sqlite_database.close()

	except sqlite3.IntegrityError as e:
		print('Sqlite Error: ', e.args[0])  # error output


# write static HTML file subroutine
def write_static_html_file(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST, LINEAR_ACTUATOR_RUN_TIME, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE, WEBPAGE_HEADER_VALUE, MINIMUM_LUMINOSITY_SENSOR_VALUE, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT, MINIMUM_TEMPERATURE_ACTUATOR_RETRACT, MINIMUM_HUMIDITY_ACTUATOR_RETRACT, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_ACTUATOR_EXTEND, MINIMUM_HUMIDITY_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_OUTPUT_ONE_ON, MINIMUM_HUMIDITY_OUTPUT_ONE_ON, MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF, MINIMUM_HUMIDITY_OUTPUT_ONE_OFF, MINIMUM_TEMPERATURE_OUTPUT_TWO_ON, MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED):
	# begin file write of static HTML file to the web server root
	static_html_file_handle = open(STATIC_WEBPAGE_FILE_NAME, "w")

	static_html_file_handle.write("""
	<html>

	<head>
	  <style>
	   table, th, td{
		border: 1px solid #333;
	   }
	  </style>

	<meta http-equiv="refresh" content="600">

	<title>Greenhouse Automation System Status Information</title></head>

	<body bgcolor="#CCFFFF">
	""")

	static_html_file_handle.write('<h3 align="center">')
	static_html_file_handle.write(WEBPAGE_HEADER_VALUE)
	static_html_file_handle.write('<br>Status Information</h3>')

	static_html_file_handle.write(
		'<center><a href="/greenhousehigh.jpg"><img src="/greenhouselow.gif" alt="Greenhouse Camera Image - Animated GIF file"  height="240" width="320"><br>Click for high resolution</center></a>')
	static_html_file_handle.write('<center><table>')
	static_html_file_handle.write(
		'<caption>Current Environmental Data</caption>')
	static_html_file_handle.write(
		'<tr><th>Reading Type</th><th>Value</th></tr>')

	current_luminosity_sensor_value = str(current_luminosity_sensor_value)
	static_html_file_handle.write('<tr><td>')
	static_html_file_handle.write('Luminosity</td><td>')
	static_html_file_handle.write('<a href="')
	static_html_file_handle.write(GRAPH_IMAGE_LUMINOSITY_URL_FILE_NAME)
	static_html_file_handle.write('">')
	static_html_file_handle.write('<img src="')
	static_html_file_handle.write(GRAPH_IMAGE_LUMINOSITY_URL_FILE_NAME)
	static_html_file_handle.write(
		'" alt="Greenhouse Luminosity Last 1000 Data Points" height="240" width="320"></a><br><center>')
	static_html_file_handle.write(current_luminosity_sensor_value)
	static_html_file_handle.write('VDC</center></td></tr>')

	current_temperature_sensor_value = str(current_temperature_sensor_value)
	static_html_file_handle.write('<tr><td>Temperature</td><td>')
	static_html_file_handle.write('<a href="')
	static_html_file_handle.write(GRAPH_IMAGE_TEMPERATURE_URL_FILE_NAME)
	static_html_file_handle.write('">')
	static_html_file_handle.write('<img src="')
	static_html_file_handle.write(GRAPH_IMAGE_TEMPERATURE_URL_FILE_NAME)
	static_html_file_handle.write(
		'" alt="Greenhouse Temperature Last 1000 Data Points" height="240" width="320"></a><br><center>')
	static_html_file_handle.write(current_temperature_sensor_value)
	static_html_file_handle.write('F</center></td></tr>')

	current_humidity_sensor_value = str(current_humidity_sensor_value)
	static_html_file_handle.write('<tr><td>Humidity</td><td>')
	static_html_file_handle.write('<a href="')
	static_html_file_handle.write(GRAPH_IMAGE_HUMIDITY_URL_FILE_NAME)
	static_html_file_handle.write('">')
	static_html_file_handle.write('<img src="')
	static_html_file_handle.write(GRAPH_IMAGE_HUMIDITY_URL_FILE_NAME)
	static_html_file_handle.write(
		'" alt="Greenhouse Humidity Last 1000 Data Points" height="240" width="320"></a><br><center>')
	static_html_file_handle.write(current_humidity_sensor_value)
	static_html_file_handle.write('%</center></td></tr>')

	current_soil_moisture_sensor_value = str(current_soil_moisture_sensor_value)
	static_html_file_handle.write('<tr><td>Soil moisture</td><td>')
	static_html_file_handle.write('<a href="')
	static_html_file_handle.write(GRAPH_IMAGE_SOIL_MOISTURE_URL_FILE_NAME)
	static_html_file_handle.write('">')
	static_html_file_handle.write('<img src="')
	static_html_file_handle.write(GRAPH_IMAGE_SOIL_MOISTURE_URL_FILE_NAME)
	static_html_file_handle.write(
		'" alt="Greenhouse Soil Moisture Last 1000 Data Points" height="240" width="320"></a><br><center>')
	static_html_file_handle.write(current_soil_moisture_sensor_value)
	static_html_file_handle.write('VDC</center></td></tr>')

	static_html_file_handle.write('<tr><td>Solenoid value</td><td>')
	static_html_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
	static_html_file_handle.write('</td></tr>')

	static_html_file_handle.write('<tr><td>Linear actuator</td><td>')
	static_html_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
	static_html_file_handle.write('</td></tr>')

	static_html_file_handle.write(
		'<tr><td>Output #1 status (fan)</td><td> %s </td></tr>' % CURRENT_OUTPUT_STATUS_LIST[0])
	static_html_file_handle.write('<br>')
	static_html_file_handle.write(
		'<tr><td>Output #2 status (heat pad|grow light)</td><td> %s </td></tr>' % CURRENT_OUTPUT_STATUS_LIST[1])
	static_html_file_handle.write('<br>')
	static_html_file_handle.write('<tr><td>Output #3 status</td><td> %s </td></tr>' %
								  CURRENT_OUTPUT_STATUS_LIST[2])
	static_html_file_handle.write('</table>')

	static_html_file_handle.write('<br><br><table>')
	static_html_file_handle.write('<tr><td>CSV data file</td><td>')
	static_html_file_handle.write('<a href="/')
	static_html_file_handle.write(INDEX_LOG_DATA_CSV_URL_FILE_NAME)
	static_html_file_handle.write('">')
	static_html_file_handle.write(INDEX_LOG_DATA_CSV_URL_FILE_NAME)
	static_html_file_handle.write('</a>')

	static_html_file_handle.write('</td></tr>')
	static_html_file_handle.write('<tr><td>Seconds since the epoch</td><td>')
	static_html_file_handle.write('%s</td></tr></table>' % time.time())

	static_html_file_handle.write('<br><br><table>')
	static_html_file_handle.write(
		'<caption>Current Configuration Values</caption>')
	static_html_file_handle.write('<tr><th>Value Type</th><th>Value</th></tr>')

	LINEAR_ACTUATOR_RUN_TIME = str(LINEAR_ACTUATOR_RUN_TIME)
	static_html_file_handle.write('<tr><td>LINEAR_ACTUATOR_RUN_TIME</td><td>')
	static_html_file_handle.write(LINEAR_ACTUATOR_RUN_TIME)
	static_html_file_handle.write(' Sec</td></tr>')

	MINIMUM_LUMINOSITY_SENSOR_VALUE = str(MINIMUM_LUMINOSITY_SENSOR_VALUE)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_LUMINOSITY_SENSOR_VALUE</td><td>')
	static_html_file_handle.write(MINIMUM_LUMINOSITY_SENSOR_VALUE)
	static_html_file_handle.write('VDC</td></tr>')

	MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT = str(
		MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT</td><td>')
	static_html_file_handle.write(MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT)
	static_html_file_handle.write('VDC</td></tr>')

	MINIMUM_TEMPERATURE_ACTUATOR_RETRACT = str(MINIMUM_TEMPERATURE_ACTUATOR_RETRACT)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_TEMPERATURE_ACTUATOR_RETRACT</td><td>')
	static_html_file_handle.write(MINIMUM_TEMPERATURE_ACTUATOR_RETRACT)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_HUMIDITY_ACTUATOR_RETRACT = str(MINIMUM_HUMIDITY_ACTUATOR_RETRACT)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_HUMIDITY_ACTUATOR_RETRACT</td><td>')
	static_html_file_handle.write(MINIMUM_HUMIDITY_ACTUATOR_RETRACT)
	static_html_file_handle.write('%</td></tr>')

	MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND = str(
		MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND</td><td>')
	static_html_file_handle.write(MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND)
	static_html_file_handle.write('VDC</td></tr>')

	MINIMUM_TEMPERATURE_ACTUATOR_EXTEND = str(MINIMUM_TEMPERATURE_ACTUATOR_EXTEND)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_TEMPERATURE_ACTUATOR_EXTEND</td><td>')
	static_html_file_handle.write(MINIMUM_TEMPERATURE_ACTUATOR_EXTEND)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_HUMIDITY_ACTUATOR_EXTEND = str(MINIMUM_HUMIDITY_ACTUATOR_EXTEND)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_HUMIDITY_ACTUATOR_EXTEND</td><td>')
	static_html_file_handle.write(MINIMUM_HUMIDITY_ACTUATOR_EXTEND)
	static_html_file_handle.write('%</td></tr>')

	MINIMUM_TEMPERATURE_OUTPUT_ONE_ON = str(MINIMUM_TEMPERATURE_OUTPUT_ONE_ON)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_TEMPERATURE_OUTPUT_ONE_ON</td><td>')
	static_html_file_handle.write(MINIMUM_TEMPERATURE_OUTPUT_ONE_ON)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF = str(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF</td><td>')
	static_html_file_handle.write(MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_HUMIDITY_OUTPUT_ONE_ON = str(MINIMUM_HUMIDITY_OUTPUT_ONE_ON)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_HUMIDITY_OUTPUT_ONE_ON</td><td>')
	static_html_file_handle.write(MINIMUM_HUMIDITY_OUTPUT_ONE_ON)
	static_html_file_handle.write('%</td></tr>')

	MINIMUM_HUMIDITY_OUTPUT_ONE_OFF = str(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_HUMIDITY_OUTPUT_ONE_OFF</td><td>')
	static_html_file_handle.write(MINIMUM_HUMIDITY_OUTPUT_ONE_OFF)
	static_html_file_handle.write('%</td></tr>')

	OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY = str(OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY) # Already a string
	static_html_file_handle.write(
		'<tr><td>OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY</td><td>')
	static_html_file_handle.write(OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_TEMPERATURE_OUTPUT_TWO_ON = str(MINIMUM_TEMPERATURE_OUTPUT_TWO_ON)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_TEMPERATURE_OUTPUT_TWO_ON</td><td>')
	static_html_file_handle.write(MINIMUM_TEMPERATURE_OUTPUT_TWO_ON)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF = str(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF</td><td>')
	static_html_file_handle.write(MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_LUMINOSITY_OUTPUT_TWO_ON = str(MINIMUM_LUMINOSITY_OUTPUT_TWO_ON)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_LUMINOSITY_OUTPUT_TWO_ON</td><td>')
	static_html_file_handle.write(MINIMUM_LUMINOSITY_OUTPUT_TWO_ON)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF = str(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF</td><td>')
	static_html_file_handle.write(MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF)
	static_html_file_handle.write('F</td></tr>')

	MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN = str(
		MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN</td><td>')
	static_html_file_handle.write(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN)
	static_html_file_handle.write('VDC</td></tr>')

	MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED = str(
		MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED)
	static_html_file_handle.write(
		'<tr><td>MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED</td><td>')
	static_html_file_handle.write(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED)
	static_html_file_handle.write('VDC</td></tr>')
	static_html_file_handle.write('</table></center><br><br>')

	static_html_file_handle.write(
		'<center><a href="/wiring.png"><img src="/wiringlow.png" alt="Automation System Wiring Diagram"><a></center>')
	static_html_file_handle.write('<br><br><br><br><center><a href="/em.php">Manual Operations</a></center><br><br><br><br></body></html>')
	static_html_file_handle.close

# display the current environmental information on the 16x2 LCD screen
def display_lcd_screen_messages():

	if (DISPLAY_LCD_SCREEN_MESSAGES_ACTIVE_SWTICH is True):

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

	# call the read system control values from files on disk subroutine
	read_control_values_from_files()

	# call the read luminosity sensor value subroutine
	current_luminosity_sensor_value = read_luminosity_sensor_value()

	# call the read temperature and humidity value subroutine
	current_humidity_sensor_value, current_temperature_sensor_value = read_temperature_humidity_values()

	# call the read soil moisture sensor value subroutine
	current_soil_moisture_sensor_value = read_soil_moisture_sensor_value()

	# call the display notifications on the 16x2 LCD screen subroutine
	display_lcd_screen_messages()

	# call the display notifications in the console as wall messages subroutine
	display_console_wall_messages()


# begin the process of evaluating environmental conditions and
# respond accordingly
def evaluate_environmetnal_conditions_perform_automated_responses():

	# evaulate if we close or open the window
	if (current_luminosity_sensor_value <= MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT and
		current_temperature_sensor_value <= MINIMUM_TEMPERATURE_ACTUATOR_RETRACT and
		current_humidity_sensor_value <= MINIMUM_HUMIDITY_ACTUATOR_RETRACT and
		CURRENT_SOLENOID_VALVE_STATUS == 'Closed'
		 ):
		# retract the linear actuator and close the window
		actuator_extension_status = 'Retracted'
		CURRENT_ACTUATOR_EXTENSION_STATUS = linear_actuator_extension_retraction(actuator_extension_status)

	elif (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND and
		  current_temperature_sensor_value > MINIMUM_TEMPERATURE_ACTUATOR_EXTEND and
		  current_humidity_sensor_value > MINIMUM_HUMIDITY_ACTUATOR_EXTEND and
		  CURRENT_SOLENOID_VALVE_STATUS == 'Closed'
		  ):
		# extend the linear actuator and open the window
		actuator_extension_status = 'Extended'
		CURRENT_ACTUATOR_EXTENSION_STATUS = linear_actuator_extension_retraction(actuator_extension_status)

	# evaulate if we need to enable output #1 turn on the fan
	if (current_temperature_sensor_value >= MINIMUM_TEMPERATURE_OUTPUT_ONE_ON or
		current_humidity_sensor_value >= MINIMUM_HUMIDITY_OUTPUT_ONE_ON and
		CURRENT_SOLENOID_VALVE_STATUS == 'Closed'
		 ):
		# enable output one
		output_number = 0
		output_status = 'On'
		current_output_status = control_outputs(output_number, output_status)

	elif (current_temperature_sensor_value < MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF or
		  current_humidity_sensor_value < MINIMUM_HUMIDITY_OUTPUT_ONE_OFF
		  ):
		# disable output one
		output_number = 0
		output_status = 'Off'
		current_output_status = control_outputs(output_number, output_status)

	# evaluate if temperature controls output two
	if (OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY == 'Temperature'):

		# evaulate if we need to enable output #2 turn on the USB heating pad
		if (current_temperature_sensor_value <= MINIMUM_TEMPERATURE_OUTPUT_TWO_ON):
			# enable output two
			output_number = 1
			output_status = 'On'
			current_output_status = control_outputs(output_number, output_status)

		# evaulate if we need to disable output #2 turn off the USB heating pad
		elif (current_temperature_sensor_value > MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF):
			# disable output two
			output_number = 1
			output_status = 'Off'
			current_output_status = control_outputs(output_number, output_status)

		# evaluate if luminosity controls output two
	elif (OUTPUT_TWO_CONFIGURATION_VALUE_BETWEEN_TEMPERATURE_OR_LUMINOSITY == 'Luminosity'):
	
		# evaulate if we need to enable output #2 turn on the grow light
		if (current_luminosity_sensor_value <= MINIMUM_LUMINOSITY_OUTPUT_TWO_ON):
			# enable output two
			output_number = 1
			output_status = 'On'
			current_output_status = control_outputs(output_number, output_status)

		# evaulate if we need to disable output #2 turn off the grow light
		elif (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_OUTPUT_TWO_OFF):
			# disable output two
			output_number = 1
			output_status = 'Off'
			current_output_status = control_outputs(output_number, output_status)

	# evaluate if the solenoid valve should be open or closed
	if (current_soil_moisture_sensor_value >= MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN):
		# disable output one
		output_number = 0
		output_status = 'Off'
		current_output_status = control_outputs(output_number, output_status)
		# enable relay three opening the solenoid valve
		solenoid_valve_status = 'Open'
		solenoid_valve_operation(solenoid_valve_status)

	elif (current_soil_moisture_sensor_value < MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED):
		# disable relay three closing the solenoid valve
		solenoid_valve_status = 'Closed'
		solenoid_valve_operation(solenoid_valve_status)



# begin HTML, Sqlite database, CSV file, and graph image updates
def perform_write_html_database_csv_graph_image_update_process():

	# call the write static HTML output file subroutine
	write_static_html_file(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value, CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST, LINEAR_ACTUATOR_RUN_TIME, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE, WEBPAGE_HEADER_VALUE, MINIMUM_LUMINOSITY_SENSOR_VALUE, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT, MINIMUM_TEMPERATURE_ACTUATOR_RETRACT,
						MINIMUM_HUMIDITY_ACTUATOR_RETRACT, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_ACTUATOR_EXTEND, MINIMUM_HUMIDITY_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_OUTPUT_ONE_ON, MINIMUM_HUMIDITY_OUTPUT_ONE_ON, MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF, MINIMUM_HUMIDITY_OUTPUT_ONE_OFF, MINIMUM_TEMPERATURE_OUTPUT_TWO_ON, MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED)

	# call the write database table subroutine
	write_database_output(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value,
						CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

	# call the write CSV output file subroutine
	write_csv_output_file(current_luminosity_sensor_value, current_temperature_sensor_value, current_humidity_sensor_value, current_soil_moisture_sensor_value,
					   CURRENT_SOLENOID_VALVE_STATUS, CURRENT_ACTUATOR_EXTENSION_STATUS, CURRENT_OUTPUT_STATUS_LIST)

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
read_values_display_messages()

# begin evaluating environmental conditions and performing
# automation responses and configured
evaluate_environmetnal_conditions_perform_automated_responses()

# begin HTML index file, Sqlite database file, CSV file, and graph
# image file updates
perform_write_html_database_csv_graph_image_update_process()

##################################################################
### End value read, notification, evaluation, update process ###
##################################################################

