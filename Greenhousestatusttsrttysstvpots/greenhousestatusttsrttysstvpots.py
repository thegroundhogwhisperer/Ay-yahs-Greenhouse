#!/usr/bin/env python
# encoding: utf-8
#
######################################################################
## Application file name: greenhousestatusttsrttysstvpots.py	    ##
## Description: A component of Ay-yahs-Greenhouse Automation System ##
## Description: Combines text-to-speeh, RTTY, SSTV audio as a	    ##
## Description: single audio file for use with play_audio.py	    ##
## Version: 1.04						    ##
## Project Repository: https://git.io/fhhsY			    ##
## Copyright (C) 2019 The Groundhog Whisperer			    ##
######################################################################
#
#
# For more information about the play_audio.py Python code please reference
# this: https://github.com/pradeesi/play_audio_over_phone_line 
# and this: https://iotbytes.wordpress.com/play-audio-file-on-phone-line-with-raspberry-pi/
#
# Produces: Greenhouse envrionmental data as text-to-speech audio, 
# RTTY audio, and SSTV audio as a single audio file played by 
# play_audio.py via a modem connected to a POTS (plain old telephone
# service) landline.
#
# greenhousestatusttsrttysstvpots.py is a Python script that retrieves
# the latest greenhouse environmental data produced by
# /Greenhouse/greenhouse.py in CSV format and produces text-to-speech
# audio output and RTTY audio output greenhousestatusttsrttysstvpots.py
# then retrieves an image file produced by /Greenhouse/camera.py and
# produces SSTV audio output. Both the CSV file and image file are
# retrieved using the wget application. Text-to-speech audio
# is produced using the Ubuntu speech-dispatcher. RTTY audio data
# is produced using the minimodem application. SSTV audio data is
# produced using the PySSTV Puython class. Audio from the
# text-to-speech output, RTTY output and SSTV output are concatenated
# into one audio file that is played using the using the play_audio.py
# Python application when an incoming call is detected.
#
# Example greenhousestatusttsrttysstvpots.py execution via a crontab
# executed every 20th minute.
#
# */20 * * * * /usr/bin/python /home/username/greenhousestatusttsrttysstvpots.py &
#
# To execute play_audio.py without administrative privilages the user account executing play_audio.py
# will have to be granted privilage to the dialout users group. The USB modem /dev/ttyACM0 is 
# attached to this access group. Add the current user to the dialout group using the usermod 
# command. E.g:
# sudo usermod -a -G dialout $USER
# or
# sudo usermod -a -G dialout username
# To configure cron to execute the play_audio.py script at boot perform the following:
# crontab -e
#
# @reboot /usr/bin/python /home/username/greenhousestatusttsrttysstvpots.py &
#

import os
import subprocess
from subprocess import call
import time
from PIL import Image, ImageDraw, ImageFont
from pysstv.color import PD90
import pysstv.sstv

# Remote CSV file URL (e.g. http://192.168.1.118/index.csv)
REMOTE_CSV_FILE_PATH_URL = "http://localhost/index.csv"

# Local copy of the remotely fetched greenhouse.csv file
LOCAL_CSV_FILE_NAME = "/home/username/indexpots.csv"

# Remote image file URL (e.g. http://192.168.1.118/greenhousehigh.jpg)
REMOTE_IMAGE_FILE_PATH_URL = "http://localhost/greenhousehigh.jpg"

# Local copy of the remotely fetched greenhouse image file
LOCAL_IMAGE_FILE_NAME = "/home/username/greenhousehighpots.jpg"

# Call sign transparent image overlay sized for PD90 SSTV
LOCAL_IMAGE_FILE_NAME_OVERLAY = "/home/username/overlaypots.png"

# Greenhouse image file converted to png format with an overlay for SSTV
LOCAL_IMAGE_FILE_NAME_PNG = "/home/username/greenhousehighpots.png"

# Path and name of the temporary TTS audio file
LOCAL_AUDIO_FILE_NAME_TTS = '/home/username/ttspots.wav'

# Path and name of the temporary TTS audio file resampled at a rate of 8000Hz
LOCAL_AUDIO_FILE_NAME_TTS_8000 = '/home/username/ttspots8000.wav'

# Path and name of the temporary RTTY modem audio file
LOCAL_AUDIO_FILE_NAME_RTTY = '/home/username/broadcastpots.wav'

# Path and name of the temporary RTTY modem audio file resampled at a rate of 8000Hz
LOCAL_AUDIO_FILE_NAME_RTTY_8000 = '/home/username/broadcastpots8000.wav'

# Path and name of the temporary SSTV audio file
LOCAL_AUDIO_FILE_NAME_SSTV = '/home/username/greenhousesstvpots.wav'

# Path and name of the temporary SSTV audio file resampled at a rate of 8000Hz
LOCAL_AUDIO_FILE_NAME_SSTV_8000 = '/home/username/greenhousesstvpots8000.wav'

# Path and name of the temporary concatendated audio file containing all three audio files
LOCAL_CONCATENATED_AUDIO_FILE_NAME = '/home/username/greenhouseanswer.wav'

# Path and name of the temporary text file containing the RTTY message content
LOCAL_TEMP_TEXT_FILE = '/home/username/temptextpots.txt'

# Minimodem baud rate speed argument (e.g. 1200, 300, RTTY)
MINIMODEM_SPEED_ARGUMENT = "RTTY"

# Execute the wget command to fetch and store the latest index.csv 
# and greenhousehigh.jpg from the automation system and generate
# TTS, RTTY, and SSTV audio output as a file.
def fetch_image_fetch_csv_generate_tts_rtty_sstv_ouput_content():

	# Fetch the camera image file to be broadcast as SSTV data
	wget_command_line_image = ["wget", "--tries=1","-N", "--no-if-modified-since", REMOTE_IMAGE_FILE_PATH_URL, "-O", LOCAL_IMAGE_FILE_NAME]
	wget_download_greenhouse_image_data_run_process = subprocess.Popen(wget_command_line_image).communicate() 

	# Define the variable line
	line = None
	
	# Fetch the CSV file to be broadcast as text-to-speech audio and RTTY data
	wget_command_line_csv = ["wget", "--tries=1","-N", "--no-if-modified-since", REMOTE_CSV_FILE_PATH_URL, "-O", LOCAL_CSV_FILE_NAME]
	wget_download_greenhouse_csv_data_run_process = subprocess.Popen(wget_command_line_csv).communicate() 

	# Try to read the local file do not die if the file does not exist
	try:
		with open(LOCAL_CSV_FILE_NAME, "r") as f:

			for line in f: pass
			# Read the last line of the CSV file containing the most recently recorded environmental values
			last_line_csv_file = line

	except IOError:
		return 'error'

	if not last_line_csv_file or len(last_line_csv_file) < 1:
		# If the file read failed to read go back to sleep and try again
		exit()

	# Remove new line char
	last_line_csv_file = last_line_csv_file.replace('\n', '')

	# Remove single quotes
	last_line_csv_file = last_line_csv_file.replace("'", "")

	# Remove double quotes
	last_line_csv_file = last_line_csv_file.replace('"', '')

	# Split at commas
	csv_values = last_line_csv_file.split(",")

	current_luminosity_sensor_value = csv_values[0]
	current_temperature = csv_values[1]
	current_humidity = csv_values[2]
	current_soil_moisture_sensor_value = csv_values[3]
	current_solenoid_valve_status = csv_values[4]
	current_actuator_extension_status = csv_values[5]
	current_output_one_status = csv_values[6]
	current_output_two_status = csv_values[7]
	current_output_three_status = csv_values[8]
	seconds_since_the_epoch = csv_values[9]

	text_to_speech_message_content = '"Hello. Thank you for calling Ay-yahs greenhouse. Greetings of peace and goodwill to all! No one is available to take your call now except, us plants. On that note, lets see whats going on in the greenhouse. The current greenhouse environmental status is as follows: Light dependent resistor at: %s volts, Temperature at: %s degrees, Humidity at: %s percent, Soil moisture sensor at: %s volts, Solenoid valve is: %s, Linear actuator is: %s, Output one is: %s, Output two is: %s, Output three is: %s, Seconds since the Unix slash Posix epoch: %s. This message will now be followed by a R,T,T,Y, audio trasnmission and a S,S,T,V, transmission. So get you DroidRTTY and your Robot 36 apps ready. "' \
										% (current_luminosity_sensor_value, current_temperature, current_humidity,
											current_soil_moisture_sensor_value, current_solenoid_valve_status,
											current_actuator_extension_status, current_output_one_status, current_output_two_status,
											current_output_three_status, seconds_since_the_epoch)

	rtty_modem_message_content = '"Begin Transmission Greetings of peace and goodwill to all! The current greenhouse environmental status is as follows LDR at %s volts, Temp. at %s degrees, Humidity at %s percent, Soil moisture sensor at %s volts, Solenoid valve is %s, Linear actuator is %s, Output one is %s, Output two is %s, Output three is %s, Seconds since the Unix POSIX epoch %s. End Transmission."' \
										% (current_luminosity_sensor_value, current_temperature, current_humidity,
											current_soil_moisture_sensor_value, current_solenoid_valve_status,
											current_actuator_extension_status, current_output_one_status, current_output_two_status,
											current_output_three_status, seconds_since_the_epoch)

	# Create the transparent image overlay containg the call sign and current greenhouse data
	# Open the image overlay file
	image_overlay_object = Image.new('RGBA', (320, 256), (255, 0, 0, 0))
	# Define the font and size used
	font_object = ImageFont.truetype("Courier_New_Bold.ttf", 59)
	# Define the text fill color
	letter_fill_color = "black"
	# Define the text outline color
	letter_outline_color = "white"
	# Define the call sign drawn on the image overlay
	sstv_call_sign = "Ay-yah"

	text_value = sstv_call_sign
	# Set the draw location for the first call sign to the upper left
	x, y = 3, -11
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	# Set the draw location for the second call sign to the lower right
	x, y = 110, 204
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	# Deduce the font size
	font_object = ImageFont.truetype("Courier_New_Bold.ttf", 25)

	text_value = "LDR:%sV" % str(current_luminosity_sensor_value)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 40
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "TEMP:%sF" % str(current_temperature)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 60
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "HUM:%s%%" % str(current_humidity)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 80
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "SOIL:%sV" % str(current_soil_moisture_sensor_value)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 100
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "VALVE:%s" % str(current_solenoid_valve_status)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 120
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "ACT:%s" % str(current_actuator_extension_status)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 140
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "OUT1:%s" % str(current_output_one_status)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 160
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	text_value = "OUT2:%s" % str(current_output_two_status)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 180
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	# Reduce the font size
	font_object = ImageFont.truetype("Courier_New_Bold.ttf", 15)

	text_value = "%s" % str(seconds_since_the_epoch)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 202
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	# Save the image overlay file
	image_overlay_object.save(LOCAL_IMAGE_FILE_NAME_OVERLAY)

	# Generate the text-to-speech audio notification using espeak
	audio_notification_command_line = ['/usr/bin/espeak', '-a', '110', '-s', '145', text_to_speech_message_content, '-w', LOCAL_AUDIO_FILE_NAME_TTS]
	# Execute the process on the operating system
	text_to_speech_current_conditions_run_process = subprocess.Popen(audio_notification_command_line).communicate()

	# Write the RTTY message content to a text file sent to minimodem using cat
	file_handle = open(LOCAL_TEMP_TEXT_FILE, 'w') 
	file_handle.write(rtty_modem_message_content)
	file_handle.close()

	# Generate the RTTY audio file using minimodem
	minimodem_command = "/usr/bin/minimodem"
	minimodem_read_write_argument = "--write"
	minimodem_file_argument = "-f"
	minimodem_command = "%s %s %s %s %s" % (minimodem_command, minimodem_read_write_argument, MINIMODEM_SPEED_ARGUMENT, minimodem_file_argument, LOCAL_AUDIO_FILE_NAME_RTTY)
	cat_command_binary = "/bin/cat"
	cat_content_text_file = LOCAL_TEMP_TEXT_FILE
	cat_command_redirect = "|"
	cat_command = "%s %s %s" % (cat_command_binary, cat_content_text_file, cat_command_redirect)
	minimodem_command_line = "%s %s" % (cat_command, minimodem_command)

	# Execute the process on the os
	call(minimodem_command_line, shell=True)

	# Generate the SSTV audio file using PySSTV
	# Open the call sign image overlay file
	imgoverlay = Image.open(LOCAL_IMAGE_FILE_NAME_OVERLAY)
	# Open the greenhouse camera image file
	imgcam = Image.open(LOCAL_IMAGE_FILE_NAME)
	# Resize the greenhouse camera image to PD90 SSTV format
	imgcam = imgcam.resize((PD90.WIDTH, PD90.HEIGHT))
	# Use PIL to paste the overlay image in place
	imgcam.paste(imgoverlay, (0, 0), imgoverlay)
	# Use PySSTV to covert the image to PD90 SSTV format
	sstv = PD90(imgcam, 44100, 16)
	# Write the modified image file to disk
	imgcam.save(LOCAL_IMAGE_FILE_NAME_PNG, "PNG")
	# Generate the WAV audio containing the SSTV transmission
	sstv.write_wav(LOCAL_AUDIO_FILE_NAME_SSTV)

	resample_tts_audio_file_command_line = ['/usr/bin/sox', LOCAL_AUDIO_FILE_NAME_TTS, '-r', '8000', '-e', 'unsigned', LOCAL_AUDIO_FILE_NAME_TTS_8000]
	# Execute the process on the os
	resample_audio_file_run_process = subprocess.Popen(resample_tts_audio_file_command_line).communicate()

	resample_rtty_audio_file_command_line = ['/usr/bin/sox', LOCAL_AUDIO_FILE_NAME_RTTY, '-r', '8000', '-e', 'unsigned', LOCAL_AUDIO_FILE_NAME_RTTY_8000, 'gain', '-10']
	# Execute the process on the os
	resample_audio_file_run_process = subprocess.Popen(resample_rtty_audio_file_command_line).communicate()

	resample_sstv_audio_file_command_line = ['/usr/bin/sox', LOCAL_AUDIO_FILE_NAME_SSTV, '-r', '8000', '-e', 'unsigned', LOCAL_AUDIO_FILE_NAME_SSTV_8000, 'gain', '-10']
	# Execute the process on the os
	resample_audio_file_run_process = subprocess.Popen(resample_sstv_audio_file_command_line).communicate()

	# Concatenate the three audio files into one audio file to be played
	# by play_audio.py when an incoming call is received on via the modem
	concatenate_audio_files_command_line = ['/usr/bin/sox', LOCAL_AUDIO_FILE_NAME_TTS_8000, LOCAL_AUDIO_FILE_NAME_RTTY_8000, LOCAL_AUDIO_FILE_NAME_SSTV_8000, '-e', 'unsigned', LOCAL_CONCATENATED_AUDIO_FILE_NAME]
	# execute the process on the os
	concatenate_audio_files_run_process = subprocess.Popen(concatenate_audio_files_command_line).communicate()


# The main subroutine
def main_subroutine():
	# Call the subroutine to fetch the last recorded temperature
	# and then play the audio notification
	fetch_image_fetch_csv_generate_tts_rtty_sstv_ouput_content()

# Call the main subroutine
main_subroutine()

