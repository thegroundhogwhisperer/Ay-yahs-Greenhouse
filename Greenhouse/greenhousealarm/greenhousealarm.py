#!/usr/bin/env python
# encoding: utf-8

# greenhousealarm.py
# Copyright (C) 2019 The Groundhog Whisperer
# greenhousealarm.py is a Python script that retrieves the latest
# greenhouse environmental data produced by /Greenhouse/greenhouse.py
# in CSV format using the wget application. greenhousealarm.py
# evaluates the last recorded temperature value and sounds an
# audible notification using the Ubuntu speech-dispatcher when
# the temperature value is not between the minimum and maximum
# threshold.

# install using crontab
# crontab -e
# */2 * * * * python3 /home/username/greenhousealarm/greenhousealarm.py

import os
import subprocess

# minimum temperature value to sound alarm
MINIMUM_TEMPERATURE_ALARM = 33

# maximum temperature value to sound alarm
MAXIMUM_TEMPERATURE_ALARM = 90

# local copy of the remotely fetched greenhouse.csv file
LOCAL_FILE_NAME = "/home/username/greenhousealarm/index.csv"

# remote CSV file URL (e.g. http://192.168.1.118/index.csv)
REMOTE_FILE_PATH_URL = "http://localhost/index.csv"

# execute the wget command to fetch and store the latest index.csv from the automation system
def fetch_csv_file_read_last_temperature():

    wget_command_line = ["wget", "--tries=1","-N", "--no-if-modified-since", REMOTE_FILE_PATH_URL, "-O", LOCAL_FILE_NAME]
    p = subprocess.Popen(wget_command_line).communicate() 

    # try to read the local file do not die if the file does not exist
    try:
        with open(LOCAL_FILE_NAME, "r") as f:

            for line in f: pass
            last_line_csv_file = line

    except IOError:
        return 'error'

    # split at commas
    csv_values = last_line_csv_file.split(",")
    current_greenhouse_temperature = csv_values[2].replace('"', '')
    current_greenhouse_temperature = int(float(current_greenhouse_temperature))
    # call the subroutine to evaluate alarm conditions
    compare_temperature_status_minimum_maximum(current_greenhouse_temperature)

# call the desktop notification program and the speech-dispatcher for text-to-speech
def audio_notification_text_to_speech(text_to_speech_message_content):

    audio_notification_command_line = ['spd-say', '--wait', text_to_speech_message_content]
    # execute the process on the os
    p = subprocess.Popen(audio_notification_command_line)


# evaluate temperature alarm status
def compare_temperature_status_minimum_maximum(current_greenhouse_temperature):

    if (current_greenhouse_temperature < MINIMUM_TEMPERATURE_ALARM and current_greenhouse_temperature is not None):
        alarm_temperature_difference = MINIMUM_TEMPERATURE_ALARM - current_greenhouse_temperature
        text_to_speech_message_content = '"Attention! Attention! Attention! The current greenhouse temperature is: %d degrees. The current minimum temperature alarm is set at: %d degrees. That is a temperature difference of %d degrees. The current temperature is too low! The little plants will freeze!"' % (current_greenhouse_temperature, MINIMUM_TEMPERATURE_ALARM, alarm_temperature_difference)
        audio_notification_text_to_speech(text_to_speech_message_content)

    elif (current_greenhouse_temperature > MAXIMUM_TEMPERATURE_ALARM and current_greenhouse_temperature is not None):
          alarm_temperature_difference = current_greenhouse_temperature - MAXIMUM_TEMPERATURE_ALARM
          text_to_speech_message_content = '"Attention! Attention! Attention! The current greenhouse temperature is: %d degrees. The current maximum temperature alarm is set at: %d degrees. That is a temperature difference of %d degrees. The current temperature is too high! The little plants will wither!"' % (current_greenhouse_temperature, MAXIMUM_TEMPERATURE_ALARM, alarm_temperature_difference)
          audio_notification_text_to_speech(text_to_speech_message_content)

# call the subroutine to fetch the last recorded temperature
# and then evaluate if an audible alarm notification is needed
fetch_csv_file_read_last_temperature()




