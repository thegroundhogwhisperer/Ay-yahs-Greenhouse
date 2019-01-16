#!/usr/bin/env python
# encoding: utf-8

# greenhouseconditionstts.py
# Copyright (C) 2019 The Groundhog Whisperer
# greenhouseconditionstts.py is a Python script that retrieves the
# latest greenhouse environmental data produced by
# /Greenhouse/greenhouse.py in CSV format using the wget
# application. greenhouseconditionstts.py then reads the current
# conditions aloud using the Ubuntu speech-dispatcher for 
# text-to-speech.

# The following crontab 
# note: the eval command specifies which display notify-send will use for alerts
# install using crontab
# $ crontab -e
# 0 18 * * * eval "export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME gnome-session)/environ)"; python3 /home/username/greenhousealarm/greenhousealarm-notify-send.py
# 0 23 * * * eval "export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME gnome-session)/environ)"; python3 /home/username/greenhousealarm/greenhousealarm-notify-send.py


import os
import subprocess

# local copy of the remotely fetched greenhouse.csv file
LOCAL_FILE_NAME = "/home/crazypotato/greenhousealarm/index.csv"

# remote CSV file URL (e.g. http://192.168.1.118/index.csv)
REMOTE_FILE_PATH_URL = "http://localhost/a/index.csv"

# execute the wget command to fetch and store the latest index.csv from the automation system
def fetch_csv_file_read_last_environmental_record():

    wget_command_line = ["wget", "--tries=1","-N", "--no-if-modified-since", REMOTE_FILE_PATH_URL, "-O", LOCAL_FILE_NAME]
    p = subprocess.Popen(wget_command_line).communicate() 

    # try to read the local file do not die if the file does not exist
    try:
        with open(LOCAL_FILE_NAME, "r") as f:

            for line in f: pass
            last_line_csv_file = line

    except IOError:
        return 'error'

    # remove new line char
    last_line_csv_file = last_line_csv_file.replace('\n', '')

    # remove single quotes
    last_line_csv_file = last_line_csv_file.replace("'", "")

    # remove double quotes
    last_line_csv_file = last_line_csv_file.replace('"', '')

    # split at commas
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

    print(current_luminosity_sensor_value, current_temperature, current_humidity,
          current_soil_moisture_sensor_value, current_solenoid_valve_status,
          current_actuator_extension_status, current_output_one_status, current_output_two_status,
          current_output_three_status, seconds_since_the_epoch)


    text_to_speech_message_content = '"November Oscar Charlie Alpha Lima Lima. \
                                      Current greenhouse environmental status, \
                                      Light dependent resistor at: %s volts, \
                                      Temperature at: %s degrees, \
                                      Humidity at: %s percent, \
                                      Soil moisture sensor at: %s volts, \
                                      Solenoid valve is: %s, \
                                      Linear actuator is: %s, \
                                      Output one is: %s, \
                                      Output two is: %s, \
                                      Output three is: %s, \
                                      Seconds since the epoch: %s. \
                                      November Oscar Charlie Alpha Lima Lima" \
                                      ' % (current_luminosity_sensor_value, current_temperature, current_humidity,
                                           current_soil_moisture_sensor_value, current_solenoid_valve_status,
                                           current_actuator_extension_status, current_output_one_status, current_output_two_status,
                                           current_output_three_status, seconds_since_the_epoch)

    # call the subroutine to generate text-to-speech audio and a notify bubble
    audio_notification_text_to_speech(text_to_speech_message_content)


# call the desktop notification program and the speech-dispatcher for text-to-speech
def audio_notification_text_to_speech(text_to_speech_message_content):

    audio_notification_command_line = ['spd-say', '--wait', text_to_speech_message_content]
    # execute the process on the os
    p = subprocess.Popen(audio_notification_command_line)

    # display a bubble in the gui using notify-send just for fun
    notify_send_command_line = ['notify-send', 'Current Conditions', text_to_speech_message_content]
    # execute the process on the os
    p = subprocess.Popen(notify_send_command_line)



# call the subroutine to fetch the last recorded temperature
# and then play the audio notification
fetch_csv_file_read_last_environmental_record()



