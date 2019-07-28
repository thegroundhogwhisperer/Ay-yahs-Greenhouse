#!/usr/bin/env python
# encoding: utf-8
#
######################################################################
## Application file name: camera.py				    ##
## Description: A component of Ay-yahs-Greenhouse Automation System ##
## Description: Reads luminosity sensor and produces image data     ##
## Description: from a camera.					    ##
## Version: 1.04					 	    ##
## Project Repository: https://git.io/fhhsY			    ##
## Copyright (C) 2019 The Groundhog Whisperer			    ##
######################################################################
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# This is a for-fun project created for the purpose of automating climate
# control and irrigation in a small greenhouse.  This script (camera.py)
# produces a high and low resolution .jpg image and a low resolution
# animated .gif image to the web servers root folder.  These images are
# referenced in the dynamic output produced by index.php and the desktop
# graphical client. This script reads a lumonisity sensor (light
# dependent resistor) connected to an analog to digital converter on a
# Pimoroni Automation hat and adjusts the camera shutter speed for
# high and low light conditions.
#
# Output files produced:
# greenhoushigh.jpg - Static 3280, 2464 jpeg
# greenhouslow.jpg - Static 320, 240 jpeg
# greenhouslow{0-9}.jpg - Static 320, 240 jpegs
# greenhouslow.gif - Animated 320, 240 gif

import picamera
import math
import time
import automationhat
time.sleep(0.1)  # short pause after ads1015 class creation recommended
import serial
import statistics
import subprocess
import os

# Path and file name of the low resolution .jpg output camera image
CAMERA_IMAGE_OUTPUT_FILE_NAME_LOW = '/var/www/html/greenhouselow.jpg'

# Path and file name of the high resolution .jpg output camera image
CAMERA_IMAGE_OUTPUT_FILE_NAME_HIGH = '/var/www/html/greenhousehigh.jpg'

# Path and file name of the multiple low resolution .jpg files used to
# create the animated .gif image
CAMERA_IMAGE_OUTPUT_FILE_NAME_JPGS_TO_ANIMATED_GIF = '/var/www/html/greenhouselowanim{0:04d}.jpg'

# ImageMagic command to create the animated gif using the multiple
# low resolution greenhouslow{0-9}.jpg files
OPERATING_SYSTEM_IMAGE_MAGICK_COMMAND_ANIMATE_JPGS_INTO_GIF = 'convert -delay 10 -loop 0 /var/www/html/greenhouselowanim*.jpg /var/www/html/greenhouselow.gif'

# Set the minimum luminosity sensors value at 0.01VDC
MINIMUM_LUMINOSITY_SENSOR_VALUE = 0.01

# Minimum luminosity sensor value used to determine the shutter speed
MINIMUM_LUMINOSITY_SENSOR_VALUE_HIGH_LIGHT_LEVEL = 1.4

# Camera shutter speed duing high ambient light levels
CAMERA_SHUTTER_SPEED_HIGH_LIGHT_LEVEL = 10000

# Camera shutter speed duing low ambient light levels
CAMERA_SHUTTER_SPEED_LOW_LIGHT_LEVEL = 1000

# High resolution JPG camera image width
CAMERA_IMAGE_HIGH_RESOLUTION_WIDTH = 3280

# High resolution JPG camera image height
CAMERA_IMAGE_HIGH_RESOLUTION_HEIGHT = 2464

# Low resolution animated GIF camera image width
CAMERA_IMAGE_LOW_RESOLUTION_WIDTH = 320

# Low resolution animated GIF camera image width
CAMERA_IMAGE_LOW_RESOLUTION_HEIGHT = 240


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
				print ('ADC error read LDR value less than 0.01VDC = %.3f Attempting reread' %
					  current_luminosity_sensor_value)

			if (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE):
				return(current_luminosity_sensor_value)
				break

		except RuntimeError as e:
			# print an error if the sensor read fails
			print ("ADC sensor read failed: ", e.args)


# camera capture images subroutine
def camera_capture_images():

	# Set the shutter speed relative the current light levels
	if (current_luminosity_sensor_value >= MINIMUM_LUMINOSITY_SENSOR_VALUE_HIGH_LIGHT_LEVEL):
		camera_shutter_speed = CAMERA_SHUTTER_SPEED_HIGH_LIGHT_LEVEL
	elif (current_luminosity_sensor_value < MINIMUM_LUMINOSITY_SENSOR_VALUE_HIGH_LIGHT_LEVEL):
		camera_shutter_speed = CAMERA_SHUTTER_SPEED_LOW_LIGHT_LEVEL

	camera = picamera.PiCamera()
	camera.resolution = (
		CAMERA_IMAGE_HIGH_RESOLUTION_WIDTH,
		CAMERA_IMAGE_HIGH_RESOLUTION_HEIGHT)
	camera.shutter_speed = camera_shutter_speed
	camera.iso = 400
	camera.start_preview()
	time.sleep(3)
	camera.exposure_mode = 'off'
	camera.capture(CAMERA_IMAGE_OUTPUT_FILE_NAME_HIGH)
	camera.stop_preview()
	camera.capture(
		CAMERA_IMAGE_OUTPUT_FILE_NAME_LOW,
		resize=(
			CAMERA_IMAGE_LOW_RESOLUTION_WIDTH,
			CAMERA_IMAGE_LOW_RESOLUTION_HEIGHT))
	camera.stop_preview()
	print ('Static .jpg images created.')

	for i in range(15):
		camera.capture(
			CAMERA_IMAGE_OUTPUT_FILE_NAME_JPGS_TO_ANIMATED_GIF.format(i),
			resize=(CAMERA_IMAGE_LOW_RESOLUTION_WIDTH,
					CAMERA_IMAGE_LOW_RESOLUTION_HEIGHT))
		time.sleep(2)
	os.system(OPERATING_SYSTEM_IMAGE_MAGICK_COMMAND_ANIMATE_JPGS_INTO_GIF)
	print ('Animated .gif image created.')

	
	
# call the read luminosity sensor value subroutine
current_luminosity_sensor_value = read_luminosity_sensor_value()

# call the camera capture images subroutine
camera_capture_images()


