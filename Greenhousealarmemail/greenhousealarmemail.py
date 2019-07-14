#!/usr/bin/env python3
# encoding: utf-8

# greenhousealarmemail.py Version 1.02 - Ay-yah's Greenhouse server email/SMS alarm notification script
# This script runs on the GreenhousePi and sends email/SMS notifications when temperature values are too high
# or low or soil moisture values are too high.
# Copyright (C) 2019 The Groundhog Whisperer
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

# This is a for-fun project created for the purpose of automating climate
# control and irrigation in a small greenhouse.
#
# Example execution using cron and a crontab every thirty minutes
# */30 * * * * python /home/pi/Greenhouse/greenhousealarmemail.py

import sqlite3
from smtplib import SMTP
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.headerregistry import Address
from ssl import SSLContext, PROTOCOL_TLSv1_2

# Name of the Sqlite3 database file
SQLITE_DATABASE_FILE = '/var/www/html/greenhouse.db'

# Name of the table to be queried
DATABASE_TABLE_NAME = 'greenhouse'

# Minimum temperature to trigger an email/sms alarm notification
# When the temperature is recorded below this value send an email alert
MINIMUM_TEMPERATURE_ALARM = 32.05

# Maximum temperature to trigger an email/sms alarm notification
MAXIMUM_TEMPERATURE_ALARM = 101.99

# Maximum soil moisture to trigger an email/sms alarm notification
MAXIMUM_SOIL_MOISTURE_ALARM = 3.1

# Tag line appended to the RTTY tranmission data
email_message_tag_line = ' Alert courtesy Ay-Yah\'s Horticultural Automation Systems @GitHub: https://git.io/fhhsY'


# Read the database for the last environmental status values
def greenhousepi_server_check_values_send_email_alarm():

	# Define global variable accessible in other functions
	global current_luminosity_sensor_value
	global current_luminosity_sensor_value
	global current_temperature
	global current_humidity
	global current_soil_moisture_sensor_value
	global current_solenoid_valve_status
	global current_actuator_extension_status
	global current_output_one_status
	global current_output_two_status
	global current_output_three_status
	global record_time
	global record_date
	global list_of_greenhouse_table_rows

	# Connecting to the Sqlite3 database file
	conn = sqlite3.connect(SQLITE_DATABASE_FILE)
	database_cursor = conn.cursor()

	# Return the last row in the greenhouse table
	database_cursor.execute("SELECT * FROM " + DATABASE_TABLE_NAME + " ORDER BY id DESC LIMIT 1;".format(tn=DATABASE_TABLE_NAME, cn=id))
	last_row_exists = database_cursor.fetchone()

	if last_row_exists:

		# We do not use all of the values returned in this script
		# print('(Record Returned): {}'.format(last_row_exists))
		last_row_greenhouse_table_sqlite3 = last_row_exists
		current_database_record_id = last_row_greenhouse_table_sqlite3[0]
		current_luminosity_sensor_value = last_row_greenhouse_table_sqlite3[1]
		current_temperature = last_row_greenhouse_table_sqlite3[2]
		current_humidity = last_row_greenhouse_table_sqlite3[3]
		current_soil_moisture_sensor_value = last_row_greenhouse_table_sqlite3[4]
		current_solenoid_valve_status = last_row_greenhouse_table_sqlite3[5]
		current_actuator_extension_status = last_row_greenhouse_table_sqlite3[6]
		current_output_one_status = last_row_greenhouse_table_sqlite3[7]
		current_output_two_status = last_row_greenhouse_table_sqlite3[8]
		current_output_three_status = last_row_greenhouse_table_sqlite3[9]
		record_date = last_row_greenhouse_table_sqlite3[10]
		record_time = last_row_greenhouse_table_sqlite3[11]

	else:
		print ("Error: No last row returned!")

	# Closing the connection to the database file
	conn.close()

	# Evaluate the last known temperature value
	print ("Evaluating temperature and soil moisture\n")
	compare_temperature_status_minimum_maximum_soil_moisture_maximum(current_temperature, current_soil_moisture_sensor_value)


# evaluate temperature alarm status
def compare_temperature_status_minimum_maximum_soil_moisture_maximum(current_temperature, current_soil_moisture_sensor_value):

	# Initilize the message content variable
	email_message_content = None

	print ('Comparing current_temperature < MINIMUM_TEMPERATURE_ALARM: ', current_temperature, MINIMUM_TEMPERATURE_ALARM)

	if (current_temperature < MINIMUM_TEMPERATURE_ALARM and current_temperature is not None):
		alarm_temperature_difference = MINIMUM_TEMPERATURE_ALARM - current_temperature
		email_message_content = 'Alert! Temperature: %d F. Minimum temperature alarm: %d F. Temperature difference: %d F. Current emperature is too low! The little plants will freeze!' % (current_temperature, MINIMUM_TEMPERATURE_ALARM, alarm_temperature_difference)

	print ('Comparing current_temperature > MAXIMUM_TEMPERATURE_ALARM: ', current_temperature, MAXIMUM_TEMPERATURE_ALARM)

	if (current_temperature > MAXIMUM_TEMPERATURE_ALARM and current_temperature is not None):
		alarm_temperature_difference = current_temperature - MAXIMUM_TEMPERATURE_ALARM
		email_message_content = 'Alert! Temperature: %d F. Maximum temperature alarm: %d F. Temperature difference: %d F. The current temperature is too high! The little plants will wither!' % (current_temperature, MAXIMUM_TEMPERATURE_ALARM, alarm_temperature_difference)

	print ('Comparing current_soil_moisture_sensor_value > MAXIMUM_SOIL_MOISTURE_ALARM: ', current_soil_moisture_sensor_value, MAXIMUM_SOIL_MOISTURE_ALARM)

	if (current_soil_moisture_sensor_value > MAXIMUM_SOIL_MOISTURE_ALARM and current_greenhouse_temperature is not None):
		alarm_soil_moisture_difference = current_soil_moisture_sensor_value - MAXIMUM_SOIL_MOISTURE_ALARM
		email_message_content = 'Alert! Soil moisture: %d V. Maximum soil moisture alarm: %d V. Soil moisture difference of %d V. The current soil is too dry! The little plants will dry up!' % (current_soil_moisture_sensor_value, MAXIMUM_SOIL_MOISTURE_ALARM, alarm_soil_moisture_difference)

	if (email_message_content is not None):
		print ('Sending the following alarm notification content:', email_message_content)
		send_email_alert_notification(email_message_content)

	elif (email_message_content is None):
		print ('No alarm conditions found at this time.')


# Send an email alert notification
def send_email_alert_notification(email_message_content):

	# Creating an email object
	msg = EmailMessage()

	# Set the sender address
	msg['From'] = 'somefromaddress@email.example'

	# Set the destination addresses
        recipients = ['sometoaddress@email.example', 'sometoaddress@email.example']
        # recipients = ['sometoaddress@email.example'] # Example single recipient
	# Join the recipients addresses into one string and set the destination values
	msg['To'] = ", ".join(recipients)
	# msg['To'] = recipients # Use with only single recipient and no .join()
	# 
	# Set the message subject by slicing the message body content down
	# msg['Subject'] = email_message_content[0:33] 
	# SMS message typically have no subject
	msg['Subject'] = ""

	# Append the tag line to the message body
	email_message_content = email_message_content + email_message_tag_line
	print (email_message_content)

	# Populate the message content with message body
	msg.set_content(email_message_content) 

	# Send the email via smtp
	with SMTP(host='smtp.email.example', port=587) as smtp_server:

		try:
			# Define a secure SSL connection
			smtp_server.starttls(context=SSLContext(PROTOCOL_TLSv1_2))
			# Supply authentication credentials
			smtp_server.login(user='somefromaddress@email.example', password='shhhhapasswordvalue')
			# Send the email message
			smtp_server.send_message(msg)

		except Exception as e:

			print('Error sending email. Details: {} - {}'.format(e.__class__, e))


# Start the validation process
greenhousepi_server_check_values_send_email_alarm()



