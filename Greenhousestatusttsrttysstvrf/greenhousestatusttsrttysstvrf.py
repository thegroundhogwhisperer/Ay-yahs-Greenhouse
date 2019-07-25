#!/usr/bin/python3
# encoding: utf-8
#
######################################################################
## Application file name: greenhousestatusttsrttysstvrf.py			##
## Description: A component of Ay-yahs-Greenhouse Automation System ##
## Description: Produces GUI notification, text-to-speech, RTTY,  	##
## Description: SSTV audio for radio frequency transmission			##
## Version: 1.03													##
## Project Repository: https://git.io/fhhsY							##
## Copyright (C) 2019 The Groundhog Whisperer						##
######################################################################
#
#
# greenhousestatusttsrttysstvrf.py is a Python script that retrieves
# the latest greenhouse environmental data produced by
# /Greenhouse/greenhouse.py in CSV format and produces text-to-speech
# output and RTTY output. greenhousestatusttsrttysstvrf.py then
# retrieves an image file produced by /Greenhouse/camera.py and
# produces SSTV output. Both the CSV file and image file are
# retrieved using the wget application. A visual desktop notification
# is displayed using the notify-send application. Text-to-speech audio
# is produced using the Ubuntu speech-dispatcher. RTTY audio data
# is produced using the minimodem application. SSTV audio data is
# produced using the PySSTV Puython class. Audio from the RTTY and
# SSTV output are played using the sox applications play command
# to the default audio output device. The audio output produced
# by greenhousestatusttsrttysstvrf.py can be connected to a 
# radio in VOX (voice-operated exchange) mode allowing for
# radio frequency transmission of the current greenhouse
# environmental conditions. Before transmitting on any
# channel or frequency the channel should be monitored for at
# least 30 seconds to verify that the channel is clear/available.
# greenhousestatusttsrttysstvrf.py uses sox to achieve verification
# of the current channels availability. Sox is used to record a 60
# second sample of the current channel. Sox is then used to
# generate statistics from the audio recording to establish a
# maximum amplitude value. This maximum amplitude value is used
# to determine if the current broadcast should be deferred due
# to traffic on the channel or frequency. A maximum amplitude
# value > 0.025 is indicative of audio input/channel traffic.
# The maximum amplitude value may have to be adjusted relative
# other system audio sample configurations.

# To execute greenhousestatusttsrttysstvrf.py using a cron tab
# use a bash shell script wrapper that exports environmental
# variables to the Python script. Access to environmental 
# variables allow applications to access the desktop GUI and
# specific users audio output devices. (e.g. notify-send,
# spd-say). Please reference:
# https://askubuntu.com/questions/978382/how-can-i-show-notify-send-messages-triggered-by-crontab
# https://askubuntu.com/questions/719590/help-using-crontab-to-play-a-sound
#
# Example bash shell script gui-launcher contents
#
# #!/bin/bash -e
# # NAME: gui-launcher
# # Check whether the user is logged-in
# while [ -z "$(pgrep gnome-session -n -U $UID)" ]; do sleep 3; done
# # Export the current desktop session environment variables
# export $(xargs -0 -a "/proc/$(pgrep gnome-session -n -U $UID)/environ")
# export XDG_RUNTIME_DIR="/run/user/1000"
# export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME gnome-session)/environ)
# # Execute the input command
# nohup "$@" >/dev/null 2>&1 &
# exit 0
#
# Example greenhousestatusttsrttysstvrf.py execution via the
# bash shell wrapper script gui-launcher using a crontab
# executed every 20th minute
#
# */20 * * * * /home/username/gui-launcher "/home/username/greenhousestatusttsrttysstvrf.py"

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
LOCAL_CSV_FILE_NAME = "/home/username/index.csv"

# Remote image file URL (e.g. http://192.168.1.118/greenhousehigh.jpg)
REMOTE_IMAGE_FILE_PATH_URL = "http://localhost/greenhousehigh.jpg"

# Local copy of the remotely fetched greenhouse image file
LOCAL_IMAGE_FILE_NAME = "/home/username/greenhousehigh.jpg"

# Call sign transparent image overlay sized for PD90 SSTV
LOCAL_IMAGE_FILE_NAME_OVERLAY = "/home/username/overlay.png"

# Greenhouse image file converted to png format with an overlay for SSTV
LOCAL_IMAGE_FILE_NAME_PNG = "/home/username/greenhousehigh.png"

# Path and name of the temporary audio sample file
LOCAL_AUDIO_FILE_NAME_RECORDING = '/home/username/recording.wav'

# The maximum amplitude value returned by sox -stats to limit broadcasting on an active channel
# please note that on some system configurations calculating the midline amplitude value
# may be more useful for detecting audio input than the maximum amplitude value
MAXIMUM_AMPLITUDE_VALUE_LIMIT = .125

# Length of audio sample used to calculate the maximum amplitude value in seconds
SOX_TRIM_AUDIO_VALUE_STOP = '30'

# Path and name of the temporary RTTY modem audio file
LOCAL_AUDIO_FILE_NAME_RTTY = '/home/username/broadcast.wav'

# Path and name of the temporary SSTV modem audio file
LOCAL_AUDIO_FILE_NAME_SSTV = '/home/username/greenhousesstv.wav'

# Path and name of the temporary text file containing the RTTY message content
LOCAL_TEMP_TEXT_FILE = '/home/username/temptext.txt'

# Minimodem baud rate speed argument (e.g. 1200, 300, RTTY)
MINIMODEM_SPEED_ARGUMENT = "RTTY"

# Execute the wget command to fetch and store the latest index.csv 
# and greenhousehigh.jpg from the automation system
def fetch_image_fetch_csv_generate_gui_tts_rtty_ouput_content():

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

	text_to_speech_message_content = '"Begin transmission: Greetings of peace and goodwill to all! This is N: O: C: A: L: L: November: Oscar: Charlie: Alpha: Lima: Lima:   The current greenhouse environmental status is as follows: Light dependent resistor at: %s volts, Temperature at: %s degrees, Humidity at: %s percent, Soil moisture sensor at: %s volts, Solenoid valve is: %s, Linear actuator is: %s, Output one is: %s, Output two is: %s, Output three is: %s, Seconds since the Unix slash Posix epoch: %s. November Oscar Charlie Alpha Lima Lima: End of transmission."' \
											% (current_luminosity_sensor_value, current_temperature, current_humidity,
											current_soil_moisture_sensor_value, current_solenoid_valve_status,
											current_actuator_extension_status, current_output_one_status, current_output_two_status,
											current_output_three_status, seconds_since_the_epoch)

	notify_send_message_content = '"Light Dependent Resistor: %s volts, Temperature: %s degrees, Humidity: %s percent, Soil moisture sensor: %s volts, Solenoid valve: %s, Linear actuator: %s, Output one: %s, Output two: %s, Output three: %s, Seconds since the Unix POSIX epoch: %s"' \
										% (current_luminosity_sensor_value, current_temperature, current_humidity,
											current_soil_moisture_sensor_value, current_solenoid_valve_status,
											current_actuator_extension_status, current_output_one_status, current_output_two_status,
											current_output_three_status, seconds_since_the_epoch)

	rtty_modem_message_content = '"de NOCALL November Oscar Charlie Alpha Lima Lima de NOCALL November Oscar Charlie Alpha Lima Lima de NOCALL November Oscar Charlie Alpha Lima Lima: Begin transmission: Greetings of peace and goodwill to all! The current greenhouse environmental status is as follows: Light dependent resistor at: %s volts, Temperature at: %s degrees, Humidity at: %s percent, Soil moisture sensor at: %s volts, Solenoid valve is: %s, Linear actuator is: %s, Output one is: %s, Output two is: %s, Output three is: %s, Seconds since the Unix POSIX epoch: %s. de NOCALL November Oscar Charlie Alpha Lima Lima: End of transmission."' \
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
	sstv_call_sign = "NOCALL"

	text_value = sstv_call_sign
	# Set the draw location for the first call sign to the upper left
	x, y = 3, -11
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	# Set the draw location for the second call sign to the lower right
	x, y = 110, 204
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# Draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
	draw_image_object.text((x, y), text_value, font=font_object, fill=letter_fill_color)

	# Reduce the font size
	font_object = ImageFont.truetype("Courier_New_Bold.ttf", 25)

	text_value = "LDR:%sV" % str(current_luminosity_sensor_value)
	# Set the draw location for the first call sign to the upper left
	x, y = 3, 40
	draw_image_object = ImageDraw.Draw(image_overlay_object)
	# draw a slightly larger text object that will be the outline
	draw_image_object.text((x-1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y-1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x-1, y+1), text_value, font=font_object, fill=letter_outline_color)
	draw_image_object.text((x+1, y+1), text_value, font=font_object, fill=letter_outline_color)
	# Draw the same text object over the slightly larger text object
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
	# Draw the same text object over the slightly larger text object
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
	# Draw the same text object over the slightly larger text object
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
	# Draw the same text object over the slightly larger text object
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

	# Call the subroutine to generate notify bubble, text-to-speech, RTTY, and SSTV audio
	generate_gui_notify_bubble_text_to_speech_audio_rtty_audio_sstv_audio(text_to_speech_message_content, notify_send_message_content, rtty_modem_message_content)


# Generate the desktop GUI notify bubble, text-to-speech audio, RTTY audio, and SSTV audio
def generate_gui_notify_bubble_text_to_speech_audio_rtty_audio_sstv_audio(text_to_speech_message_content, notify_send_message_content, rtty_modem_message_content):

	# First verify the channel appears to be clear of traffic
	# Record 60 seconds of audio using sox
	# Use arecord command with -l or -L to locate values for the hw:#,# option
	# sox_record_audio_command = '/usr/bin/sox -b 32 -r 96000 -c 2 -t alsa hw:0,0 /home/usernamegreenhousettsrf/recording.wav trim 0 5'
	sox_command = '/usr/bin/sox'
	sox_bit_option = '-b'
	sox_bit_value = '32'
	sox_sample_rate_option = '-r'
	sox_sample_rate_value = '96000'
	sox_channels_audio_option = '-c'
	sox_channels_value = '2'
	sox_file_type_option = '-t'
	sox_file_type_value0 = 'alsa'
	sox_file_type_value1 = 'hw:0,0'
	sox_output_file_name = LOCAL_AUDIO_FILE_NAME_RECORDING
	sox_trim_audio_option = 'trim'
	sox_trim_audio_value_start = '0'

	record_process = subprocess.Popen([sox_command, sox_bit_option, sox_bit_value, sox_sample_rate_option, sox_sample_rate_value, sox_channels_audio_option, sox_channels_value, sox_file_type_option, sox_file_type_value0, sox_file_type_value1, sox_output_file_name, sox_trim_audio_option, sox_trim_audio_value_start, SOX_TRIM_AUDIO_VALUE_STOP])
	# Sleep until sox has finished recording before calculating statistics on the audio data
	time.sleep(int(SOX_TRIM_AUDIO_VALUE_STOP) + 3)

	# Use sox to calculate the maximum amplitude value
	# Maximum amplitude value > 0.025 = audio detected 
	sox_calculate_midline_amplitude_command = "sox %s -n stat 2>&1" % LOCAL_AUDIO_FILE_NAME_RECORDING
	command_output = subprocess.getoutput([sox_calculate_midline_amplitude_command])

	maximum_amplitude_command_output_split_once = command_output.split(':')
	maximum_amplitude_command_output_split_twice = maximum_amplitude_command_output_split_once[4].split('\n')
	maximum_amplitude_command_output_split_twice = maximum_amplitude_command_output_split_twice[0]
	maximum_amplitude_value = float(maximum_amplitude_command_output_split_twice.replace(' ', ''))
	print ('Maximum amplitude calculated at: %s' % str(maximum_amplitude_value))

	if maximum_amplitude_value is None:
		# Display a bubble in the GUI
		notify_send_message_content = '"Broadcast deferred! Unable to estimate maximum amplitude from an audio sample of the current channel."' 
		notify_send_command_line = ['notify-send', 'Broadcast deferred!', notify_send_message_content]
		print ("Exiting due to lack of sample data")
		# Execute the process on the os
		notify_send_GUI_no_data_run_process = subprocess.Popen(notify_send_command_line)
		exit()

	if maximum_amplitude_value >= MAXIMUM_AMPLITUDE_VALUE_LIMIT:
		# Display a bubble in the GUI
		notify_send_message_content = '"Broadcast deferred! Incoming transmission detected!"' 
		notify_send_command_line = ['notify-send', 'Broadcast deffered!', notify_send_message_content]
		print ("Exiting due to channel traffic")
		# Execute the process on the os
		notify_send_GUI_channel_traffic_run_process = subprocess.Popen(notify_send_command_line)
		exit()

	else:

		# Display a bubble in the gui using notify-send
		# notify_send_command_line = ['notify-send', '--urgency=critical', 'Current Greenhouse Conditions', notify_send_message_content]
		notify_send_command_line = ['notify-send', 'Current Greenhouse Conditions', notify_send_message_content]
		# Execute the process on the os
		notify_send_GUI_current_conditions_run_process = subprocess.Popen(notify_send_command_line)

		# Generate the text-to-speech audio notification
		audio_notification_command_line = ['/usr/bin/spd-say', '--wait', text_to_speech_message_content]
		# Execute the process on the os
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

		# Use sox play command to broadcast the RTTY audio output 
		audio_notification_command_line = ['/usr/bin/play', LOCAL_AUDIO_FILE_NAME_RTTY]
		# Execute the process on the os
		play_modem_rtty_file_current_conditions_run_process = subprocess.Popen(audio_notification_command_line).communicate()

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

		# Use the sox play command to broadcast the SSTV audio output 
		audio_notification_command_line = ['/usr/bin/play', LOCAL_AUDIO_FILE_NAME_SSTV]
		# Execute the process on the os
		play_modem_sstv_file_current_conditions_run_process = subprocess.Popen(audio_notification_command_line).communicate()


# The main subroutine
def main_subroutine():
	# Call the subroutine to fetch the last recorded temperature
	# and then play the audio notification
	fetch_image_fetch_csv_generate_gui_tts_rtty_ouput_content()

# Call the main subroutine
main_subroutine()

