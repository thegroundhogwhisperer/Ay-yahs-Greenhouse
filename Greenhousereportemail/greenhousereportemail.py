#!/usr/bin/env python3
# encoding: utf-8

# greenhousereportemail.py Version 1.03 - Ay-yah's GreenhousePi server email report notification script
# This script runs on the GreenhousePi and sends email reports containing system status information.
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
# Example execution using a crontab sending a status report a noon daily
# 0 12 * * * python /home/pi/Greenhouse/greenhousereportemail.py

import sqlite3
from smtplib import SMTP
from email.header import Header
from email.headerregistry import Address
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ssl import SSLContext, PROTOCOL_TLSv1_2
from email import encoders
from email import charset
import os.path
import datetime


# luminosity graph image local output file name
GRAPH_IMAGE_LUMINOSITY_FILE_NAME = "/var/www/html/ghouselumi.png"

# temperature graph image local output file name
GRAPH_IMAGE_TEMPERATURE_FILE_NAME = "/var/www/html/ghousetemp.png"

# humidity graph image local output file name
GRAPH_IMAGE_HUMIDITY_FILE_NAME = "/var/www/html/ghousehumi.png"

# soil moisture graph image local output file name
GRAPH_IMAGE_SOIL_MOISTURE_FILE_NAME = "/var/www/html/ghousesoil.png"

# greenhouse animated .gif low resolution image file
CAMERA_IMAGE_LOW_RESOLUTION_ANIMATED_GIF_FILE_NAME = "/var/www/html/greenhouselow.gif"

# greenhouse .jpg high resolution image file
CAMERA_IMAGE_HIGH_RESOLUTION_JPG_FILE_NAME = "/var/www/html/greenhousehigh.jpg"

# Name of the Sqlite3 database file
SQLITE_DATABASE_FILE = '/var/www/html/greenhouse.db'

# Name of the table to be queried
DATABASE_TABLE_NAME = 'greenhouse'

# Email message from address value
FROM_EMAIL_ADDRESS_VALUE = 'somefromaddress@email.example'

# Email message recipients destination address values
RECIPIENTS_EMAIL_ADDRESS_VALUES = ['sometoaddress@email.example', 'sometoaddress@email.example']

# SMTP email servers host name
EMAIL_SMTP_SERVER_HOST_NAME = 'smtp.email.example'

# SMTP server user name
SMTP_SERVER_LOGIN_NAME = 'somefromaddress@email.example'

# SMTP server password
SMTP_SERVER_LOGIN_PASSWORD = 'shhhhaplaintextpasswordvalue'

# Tag line appended to the email data
EMAIL_MESSAGE_TAG_LINE = 'Report notification courtesy Ay-Yah\'s Horticultural Automation Systems @GitHub: https://git.io/fhhsY'


# Read the database for the last environmental status values
def greenhousepi_server_read_values_send_email_report():

	# Define global variable accessible in other functions
	global current_luminosity_sensor_value
	global current_temperature_value
	global current_humidity_value
	global current_soil_moisture_sensor_value
	global current_solenoid_valve_status_value
	global current_actuator_extension_status_value
	global current_output_one_status_value
	global current_output_two_status_value
	global current_output_three_status_value
	global current_record_time_value
	global current_record_date_value
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
		current_database_record_id_value = last_row_greenhouse_table_sqlite3[0]
		current_luminosity_sensor_value = last_row_greenhouse_table_sqlite3[1]
		current_temperature_value  = last_row_greenhouse_table_sqlite3[2]
		current_humidity_value = last_row_greenhouse_table_sqlite3[3]
		current_soil_moisture_sensor_value = last_row_greenhouse_table_sqlite3[4]
		current_solenoid_valve_status_value = last_row_greenhouse_table_sqlite3[5]
		current_actuator_extension_status_value = last_row_greenhouse_table_sqlite3[6]
		current_output_one_status_value = last_row_greenhouse_table_sqlite3[7]
		current_output_two_status_value = last_row_greenhouse_table_sqlite3[8]
		current_output_three_status_value = last_row_greenhouse_table_sqlite3[9]
		current_record_date_value = last_row_greenhouse_table_sqlite3[10]
		current_record_time_value = last_row_greenhouse_table_sqlite3[11]
		current_record_time_value = str(current_record_time_value)


	else:
		print ("Error: No last row returned!")

	# Closing the connection to the database file
	conn.close()

	send_email_report_notification()

# Send an email alert notification
def send_email_report_notification():

	# Return the current date and time	
	current_time_stamp = datetime.datetime.today()

	# Define the text based message content
	email_message_content = "Current Status Report - Luminosity: {0} V\n Temperature: {1} F\n Humidity: {2} %\n Soil Moisture: {3} V\n Solenoid Valve: {4}\n Linear Actuator: {5}\n Output #1: {6}\n Output #2: {7}\n Output #1: {8}\n Record Date: {9}\n Record Time: {10}\n Current Timestamp: {11}\nAy-yah\'s Greenhouse Automation System Version 1.03\n\n".format(current_luminosity_sensor_value, current_temperature_value, current_humidity_value, current_soil_moisture_sensor_value, current_solenoid_valve_status_value, current_actuator_extension_status_value, current_output_one_status_value, current_output_two_status_value, current_output_three_status_value, current_record_date_value, current_record_time_value, current_time_stamp) + EMAIL_MESSAGE_TAG_LINE

	# Define the html based message content
	email_message_html_content = '<html>' \
			'<head><title>Ay-yah\'s Greenhouse Automation System Version 1.03</title>' \
			'<style>' \
			'table, th, td {' \
			'  border: 1px solid black;' \
			'  border-collapse: collapse;' \
			'}' \
			'th, td {' \
			'  padding: 10px;' \
			'}' \
			'</style>' \
			'</head>' \
			'<body>' \
			' <center>' \
			'<h1 align="center">Ay-yah\'s Greenhouse Status Report</h1>' \
			'  <table style="width:30%" align="center">' \
			'    <tr>' \
			'      <td valign="top">' \
			'<h2 align="center" valign="center">Status Information</h2>' \
			'<table style="width:20%" align="center" valign="top">' \
			'    <tr>' \
			'      <th>Reading Name</th>' \
			'      <th>Value</th>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Luminosity</td>' \
			'      <td align="center">' + \
			"{0}" \
			' V</td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Temperature</td>' \
			'      <td align="center">' \
			"{1}" \
			' F</td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Humidity</td>' \
			'      <td align="center">' \
			"{2}" \
			' %</td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Soil Moisture</td>' \
			'      <td align="center">' \
			"{3}" \
			' V</td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Solenoid Valve</td>' \
			'      <td align="center">' \
			"{4}" \
			'      </td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Linear Actuator</td>' \
			'      <td align="center">' \
			"{5}" \
			'      </td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Output One</td>' \
			'      <td align="center">'  \
			"{6}" \
			'      </td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Output Two</td>' \
			'      <td align="center">'  \
			"{7}" \
			'      </td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Output Three</td>' \
			'      <td align="center">'  \
			"{8}" \
			'      </td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Record Date</td>' \
			'      <td align="center">'  \
			"{9}" \
			'      </td>' \
			'    </tr>' \
			'    <tr>' \
			'      <td align="center">Record Time</td>' \
			'      <td align="center">' \
			"{10}" \
			'      </td>' \
			'    </tr>' \
			'  </table>' \
			' </td>' \
			' <td valign="top">' \
			'<center><h2>' \
			'</h2>' \
			'<a href="cid:5">' \
			'<img src="cid:0" alt="Greenhouse Camera Image - Animated GIF file"  height="240" width="320" border="5">' \
			'<br>Click for high resolution image</a><br>' \
			'<h2 align="center">Graphical Environmental Record<br>(24 Hours)</h2>' \
			'<table align="center">' \
			'<thead>' \
			'    <tr>' \
			'      <th>Luminosity</th>' \
		        '      <td><img src="cid:1" alt="Greenhouse Luminosity (Last 24 Hours)" height="240" width="320"></td>' \
		        '    </tr>' \
		        '    <tr>' \
		        '      <th>Temperature</th>' \
		        '      <td><img src="cid:2" alt="Greenhouse Temperature (Last 24 Hours)" height="240" width="320"></td>' \
		        '    </tr>' \
		        '    <tr>' \
		        '      <th>Humidity</th>' \
		        '      <td><img src="cid:3" alt="Greenhouse Humidity (Last 24 Hours)" height="240" width="320"></td>' \
		        '    </tr>' \
		        '    <tr>' \
		        '      <th>Soil Mositure</th>' \
		        '      <td><img src="cid:4" alt="Greenhouse Soil Moisture (Last 24 Hours)" height="240" width="320"></td>' \
		        '    </tr>' \
			' </tbody>' \
			'</table>' \
			"<center><br>This message generated: {11}<br><br>" \
			"{12}<br><br>" \
			'</center>' \
			'</body>' \
			'</html>'.format(current_luminosity_sensor_value, current_temperature_value, current_humidity_value, current_soil_moisture_sensor_value, current_solenoid_valve_status_value, current_actuator_extension_status_value, current_output_one_status_value, current_output_two_status_value, current_output_three_status_value, current_record_date_value, current_record_time_value, current_time_stamp, EMAIL_MESSAGE_TAG_LINE)


	# Create a MIMEMultipart object which will contain both email and attachment data
	msg = MIMEMultipart("alternative")
	# Set the sender address
	msg['From'] = FROM_EMAIL_ADDRESS_VALUE
	# Set the destination addresses
	recipients = RECIPIENTS_EMAIL_ADDRESS_VALUES
	# recipients = ['sometoaddress@email.example'] # Example single recipient
	# Join the recipients addresses into one string and set the destination values
	msg['To'] = ", ".join(recipients)
	# msg['To'] = recipients # Use with only single recipient and no .join()
	
	# Define the message subject
	# email_subject = "Ay-yah's Greenhouse Status Report: {0}".format(current_time_stamp)
	email_subject = "Ay-yah's Greenhouse Status Report"
	msg['Subject'] = Header(email_subject, 'utf-8').encode()

	# Create the text based message content object that is 'plain'
	msg_content = MIMEText(email_message_content, 'plain', 'utf-8')
	msg.attach(msg_content)

	# Create the html based message content object that is 'html'    
	msg_html_content = MIMEText(email_message_html_content, 'html', 'utf-8')
	msg.attach(msg_html_content)

	# Define a tuple containing all of the image files being uploaded
	image_file_name_and_path_tuple = (CAMERA_IMAGE_LOW_RESOLUTION_ANIMATED_GIF_FILE_NAME, GRAPH_IMAGE_LUMINOSITY_FILE_NAME, GRAPH_IMAGE_TEMPERATURE_FILE_NAME, GRAPH_IMAGE_HUMIDITY_FILE_NAME, GRAPH_IMAGE_SOIL_MOISTURE_FILE_NAME, CAMERA_IMAGE_HIGH_RESOLUTION_JPG_FILE_NAME)     

	# Define a counter for the loop through the tuple list
	i = 0

	# Loop through the image files listed in the tuple and upload each image as an attachment
	for image_file_path in image_file_name_and_path_tuple:

		if(os.path.isfile(image_file_path)):

			# Open the image file as a readable binary 'rb'
			image_file = open(image_file_path, 'rb')

			# Create the MIMEBase object
			image_part = MIMEImage(image_file.read(), name=image_file_path)
			image_part.add_header('Content-ID', '<'+str(i)+'>')
			image_part.add_header("Content-Disposition", "in-line", filename=image_file_path)
			image_part.add_header('X-Attachment-Id', str(i))            
			# Attach the MIMEBase object to the email message
			msg.attach(image_part)
			image_file.close()
            
			image_part_str = image_part.as_string()
			# print('Attached image file is : ' + image_file_path + ', image part string : ' + image_part_str)
			i = i + 1

	# Send the email via SMTP
	with SMTP(host=EMAIL_SMTP_SERVER_HOST_NAME, port=587) as smtp_server:

		try:
			# Define a secure SSL connection
			smtp_server.starttls(context=SSLContext(PROTOCOL_TLSv1_2))
			# Supply authentication credentials
			smtp_server.login(user=SMTP_SERVER_LOGIN_NAME, password=SMTP_SERVER_LOGIN_PASSWORD)
			# Send the email message
			smtp_server.send_message(msg)

		except Exception as e:

			print('Error sending email. Details: {} - {}'.format(e.__class__, e))


# Start the validation process
greenhousepi_server_read_values_send_email_report()



