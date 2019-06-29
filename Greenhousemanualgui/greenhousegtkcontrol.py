#!/usr/bin/env python
# encoding: utf-8

# greenhousegtkcontrol.py
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Pango
import time
import urllib2
import sqlite3
import sys

# Name of the Sqlite3 database file
SQLITE_DATABASE_FILE = 'greenhouse.db'

# Name of the table to be queried
DATABASE_TABLE_NAME = 'greenhouse'

# Number of historic environmental data rows to display in the history window =< 1500
LIMIT_NUMBER_ROWS_DISPLAYED = '1000'

# Remote IP address of the GreenhouePi
IP_GREENHOUSE_PI = '192.168.1.118'

# Timeout in seconds before urllib2 fails to fetch the remote URL 
# (e.g. Downloading a file or performing a manual greenhouse operation.)
URL_FETCH_TIMEOUT_SECONDS = 3

# Action selection input number to remote control function list
# 0/1 Turn on/off the greenhouse fan
# 2/3 Turn on/off the greenhouse light
# 4/5 Turn on/off output three
# 6/7 Open/close the water solenoid valve
# 8/9 Open/close the window
REMOTE_CONTROL_URLS = ["http://{}/openoutputonemanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/closeoutputonemanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/openoutputtwomanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/closeoutputtwomanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/openoutputthreemanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/closeoutputthreemanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/openwatermanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/closewatermanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/openwindowmanual.php".format(IP_GREENHOUSE_PI),
			"http://{}/closewindowmanual.php".format(IP_GREENHOUSE_PI)]

# Create the main GUI window class
class MyWindow(Gtk.Window):

    def __init__(self):

	print "Ready to perform manual operations."

	# Set the window title
	Gtk.Window.__init__(self, title="Ay-yah's Greenhouse Manual Operations")
	# Set the window size
	self.set_size_request(400, 300)
	# Create a a vertical container box 
	self.box = Gtk.VBox(spacing=0)
	self.add(self.box)

	# Construct a Gtk image object
	img = Gtk.Image()
	# Set the image data from the contents of a file
	img.set_from_file("greenhouselow.gif")
	# Make the object visible
	img.show()
	# Add the image to the window
	self.box.pack_start(img, True, True, 10)

	# Create some labels and add the current environmental values below the image in the main window
	label_current_luminosity_sensor_value = Gtk.Label()
        label_current_luminosity_sensor_value.set_text('Luminosity: ' + str(current_luminosity_sensor_value) + 'V')
        label_current_luminosity_sensor_value.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_luminosity_sensor_value, True, True, 0)

	label_current_temperature = Gtk.Label()
        label_current_temperature.set_text('Temperature: ' + str(current_temperature) + 'F')
        label_current_temperature.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_temperature, True, True, 0)

	label_current_humidity = Gtk.Label()
        label_current_humidity.set_text('Humidity: ' + str(current_humidity) + '%')
        label_current_humidity.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_humidity, True, True, 0)

	label_current_soil_moisture_sensor_value = Gtk.Label()
        label_current_soil_moisture_sensor_value.set_text('Soil Moisture: ' + str(current_soil_moisture_sensor_value) + 'V')
        label_current_soil_moisture_sensor_value.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_soil_moisture_sensor_value, True, True, 0)

	label_current_solenoid_valve_status = Gtk.Label()
        label_current_solenoid_valve_status.set_text('Solenoid Valve: ' + str(current_solenoid_valve_status))
        label_current_solenoid_valve_status.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_solenoid_valve_status, True, True, 0)

	label_current_actuator_extension_status = Gtk.Label()
        label_current_actuator_extension_status.set_text('Actuator: ' + str(current_actuator_extension_status))
        label_current_actuator_extension_status.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_actuator_extension_status, True, True, 0)

	label_current_output_one_status = Gtk.Label()
        label_current_output_one_status.set_text('Output One: ' + str(current_output_one_status))
        label_current_output_one_status.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_output_one_status, True, True, 0)

	label_current_output_two_status = Gtk.Label()
        label_current_output_two_status.set_text('Output Two: ' + str(current_output_two_status))
        label_current_output_two_status.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_output_two_status, True, True, 0)

	label_current_output_three_status = Gtk.Label()
        label_current_output_three_status.set_text('Output Three: ' + str(current_output_three_status))
        label_current_output_three_status.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_output_three_status, True, True, 0)

	label_current_time_readable = Gtk.Label()
        label_current_time_readable.set_text('Timestamp: ' + record_time + ' ' + record_date)
        label_current_time_readable.set_justify(Gtk.Justification.LEFT)
        self.box.pack_start(label_current_time_readable, True, True, 0)
	
	label = Gtk.Label("Please select a manual operation to perform")
        self.box.pack_start(label, True, True, 10)
        
	# Add the manual operations buttons
        self.button0 = Gtk.Button(label="Fan On (Output One On)")
        self.button0.connect("clicked", self.on_button0_clicked)
        self.box.pack_start(self.button0, True, True, 1)

        self.button1 = Gtk.Button(label="Fan Off (Output One Off)")
        self.button1.connect("clicked", self.on_button1_clicked)
        self.box.pack_start(self.button1, True, True, 1)

        self.button2 = Gtk.Button(label="Light On (Output Two On)")
        self.button2.connect("clicked", self.on_button2_clicked)
        self.box.pack_start(self.button2, True, True, 1)

        self.button3 = Gtk.Button(label="Light Off (Output Two Off)")
        self.button3.connect("clicked", self.on_button3_clicked)
        self.box.pack_start(self.button3, True, True, 1)

        self.button4 = Gtk.Button(label="Unused (Output Three On)")
        self.button4.connect("clicked", self.on_button4_clicked)
        self.box.pack_start(self.button4, True, True, 1)

        self.button5 = Gtk.Button(label="Unused (Output Three Off)")
        self.button5.connect("clicked", self.on_button5_clicked)
        self.box.pack_start(self.button5, True, True, 1)

        self.button6 = Gtk.Button(label="Open Solenoid Valve")
        self.button6.connect("clicked", self.on_button6_clicked)
        self.box.pack_start(self.button6, True, True, 1)

        self.button7 = Gtk.Button(label="Close Solenoid Valve")
        self.button7.connect("clicked", self.on_button7_clicked)
        self.box.pack_start(self.button7, True, True, 1)

        self.button8 = Gtk.Button(label="Open Window (Extend Actuator)")
        self.button8.connect("clicked", self.on_button8_clicked)
        self.box.pack_start(self.button8, True, True, 1)

        self.button9 = Gtk.Button(label="Close Window (Retract Actuator)")
        self.button9.connect("clicked", self.on_button9_clicked)
        self.box.pack_start(self.button9, True, True, 1)

	# Add some link buttons to the bottom of the main window
	# Linkbutton pointing to the given URI
        button_url0 = Gtk.LinkButton(uri="http://{}".format(IP_GREENHOUSE_PI))
        button_url0.set_label("GreenhousePi Homepage")

        # Add the button to the window
	self.box.pack_start(button_url0, True, True, 0)

	# Linkbutton pointing to the given URI
        button_url1 = Gtk.LinkButton(uri="http://{}/greenhouse.db".format(IP_GREENHOUSE_PI))
        button_url1.set_label("Download historic data .DB (SQLite3)")

        # Add the button to the window
	self.box.pack_start(button_url1, True, True, 0)

	# Linkbutton pointing to the given URI
        button_url3 = Gtk.LinkButton(uri="http://{}/index.csv".format(IP_GREENHOUSE_PI))
        button_url3.set_label("Download historic data .CSV")

        # Add the button to the window
	self.box.pack_start(button_url3, True, True, 0)

	# A linkbutton pointing to the given URI
        button_url4 = Gtk.LinkButton(uri="https://git.io/fhhsY")
        button_url4.set_label("Ay-yah's Greenhouse GitHub Repository")


    # Define the functions performed when a button is selected/clicked
    def on_button0_clicked(self, widget):
        print("Turning Fan On")
	remote_command_number_option = 0
	fetch_url_trigger_event(remote_command_number_option)

    def on_button1_clicked(self, widget):
        print("Turning Fan Off")
	remote_command_number_option = 1
	fetch_url_trigger_event(remote_command_number_option)

    def on_button2_clicked(self, widget):
        print("Turning Light On")
	remote_command_number_option = 2
	fetch_url_trigger_event(remote_command_number_option)

    def on_button3_clicked(self, widget):
        print("Turning Light Off")
	remote_command_number_option = 3
	fetch_url_trigger_event(remote_command_number_option)

    def on_button4_clicked(self, widget):
        print("Turning Unused Output Three On")
	remote_command_number_option = 4
	fetch_url_trigger_event(remote_command_number_option)

    def on_button5_clicked(self, widget):
        print("Turning Unused Output Three Off")
	remote_command_number_option = 5
	fetch_url_trigger_event(remote_command_number_option)

    def on_button6_clicked(self, widget):
        print("Opening Solenoid Valve")
	remote_command_number_option = 6
	fetch_url_trigger_event(remote_command_number_option)

    def on_button7_clicked(self, widget):
        print("Closing Solenoid Valve")
	remote_command_number_option = 7
	fetch_url_trigger_event(remote_command_number_option)

    def on_button8_clicked(self, widget):
        print("Opening Window")
	remote_command_number_option = 8
	fetch_url_trigger_event(remote_command_number_option)

    def on_button9_clicked(self, widget):
        print("Closing Window")
	remote_command_number_option = 9
	fetch_url_trigger_event(remote_command_number_option)


# Define the function called after the button selection function performing the remote URL fetch (manual operation)
def fetch_url_trigger_event(remote_command_number_option):

	print "Fetching URL: ", REMOTE_CONTROL_URLS[remote_command_number_option]

	remote_control_command_request_url = urllib2.Request(REMOTE_CONTROL_URLS[remote_command_number_option])

	try: 
		response_control_command = urllib2.urlopen(remote_control_command_request_url, timeout = URL_FETCH_TIMEOUT_SECONDS)
		object_containing_the_output_response_page = response_control_command.read()
		print "Operation successful!"
		print "URL fetch results: ", object_containing_the_output_response_page

	except urllib2.URLError as e:
		print "***Operation Failed*** An error occurred: "
		print e.reason   


# Create the history data GUI window class
class DialogWindow(Gtk.Window):

	def __init__(self):

		# Define the column header values
		columns = ["Record",
		           "LDR",
		           "Temp.",
		           "Humidity",
			   "Soil",
			   "Solenoid",
			   "Actuator",
			   "Output #1",
			   "Output #2",
			   "Output #3",
			   "Date",
			   "Time"]

		# Create a window, set the title, set the window size, and set the border width
	        Gtk.Window.__init__(self, title="Historic Environmental Record")
	        self.set_default_size(975, 350)
	        self.set_border_width(10)

		# Make the window scrollable
	        scrolled_window = Gtk.ScrolledWindow()
	        scrolled_window.set_border_width(10)
	        scrolled_window.set_policy(
	            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)

		# Define the listmodel used by the ListStore
	       	listmodel = Gtk.ListStore(int, float, float, float, float, str, str, str, str, str, str, str)

	        # Append the values in the model
	        for i in range(len(list_of_greenhouse_table_rows)):
	            listmodel.append(list(list_of_greenhouse_table_rows[i]))

	        # Create a TreeView to see the data stored in the model
	        view = Gtk.TreeView(model=listmodel)
	        # For each column
	        for i, column in enumerate(columns):
	            # Cellrenderer to render the text
	            cell = Gtk.CellRendererText()
	            # The text in all of the columns should be in boldface
	            if i is not None:
	                cell.props.weight_set = True
	                cell.props.weight = Pango.Weight.BOLD
	            # Create the column
	            col = Gtk.TreeViewColumn(column, cell, text=i)
	            # Appended the column to the TreeView
	            view.append_column(col)

	        # Create a grid to attach the widgets to
	        grid = Gtk.Grid()
	        grid.attach(view, 0, 0, 1, 1)
	
	        # Add the image to the scrolledwindow
	        scrolled_window.add_with_viewport(grid)

	        # Add the scrolledwindow to the window
	        self.add(scrolled_window)

# Define the function that downloads the image files and greenhouse.db file the queries the greenhouse.db file
def fetch_greenhouse_data():

	print "Downloading the low resolution animated .GIF image file."

	try:
		filedata = urllib2.urlopen("http://{}/greenhouselow.gif".format(IP_GREENHOUSE_PI))  
		datatowrite = filedata.read()
		with open('greenhouselow.gif', 'wb') as f:  
			f.write(datatowrite)

	except urllib2.URLError as e:
		print "Failed to download the low resolution animated .GIF image. An error occurred: "
		print e.reason   

	print "Downloading the high resolution .JPG image file."

	try:
		filedata = urllib2.urlopen("http://{}/greenhousehigh.jpg".format(IP_GREENHOUSE_PI))  
		datatowrite = filedata.read()
		with open('greenhousehigh.jpg', 'wb') as f:  
			f.write(datatowrite)

	except urllib2.URLError as e:
		print "Failed to download the high resolution .JPG image. An error occurred: "
		print e.reason   


	print "Downloading the historic environmental record greenhouse.db file."

	try:
		filedata = urllib2.urlopen("http://{}/greenhouse.db".format(IP_GREENHOUSE_PI))  
		datatowrite = filedata.read()
		with open('greenhouse.db', 'wb') as f:  
			f.write(datatowrite)

	except urllib2.URLError as e:
		print "Failed to download the historic environmental record greenhouse.db file.  An error occurred: "
		print e.reason

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

	# Return the last n number of rows from the greenhouse table
	database_cursor.execute("SELECT * FROM " + DATABASE_TABLE_NAME + " ORDER BY id DESC LIMIT " + LIMIT_NUMBER_ROWS_DISPLAYED.format(tn=DATABASE_TABLE_NAME, cn=id))
	list_of_greenhouse_table_rows = database_cursor.fetchall()

	# Return the last row in the greenhouse table
	database_cursor.execute("SELECT * FROM " + DATABASE_TABLE_NAME + " ORDER BY id DESC LIMIT 1;".format(tn=DATABASE_TABLE_NAME, cn=id))
	last_row_exists = database_cursor.fetchone()

	if last_row_exists:

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
		print "Error: No last row returned!"

	# Closing the connection to the database file
	conn.close()


# Create the high resolution camera image GUI window class
class Large_Image_Window(Gtk.Window):

    def __init__(self):

	# Create the window object, set the title, and set the size
        Gtk.Window.__init__(self, title="High Resolution Camera Image")
	self.set_default_size(640, 480)

	# Create a scrollable window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        # There is always the scrollbar automaticaly or none if not needed
        scrolled_window.set_policy(
            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)

	# Construct a Gtk image object
	img = Gtk.Image() 
	# Set the image data from the contents of a file
	img.set_from_file("greenhousehigh.jpg") 

        # Add the image to the scrolledwindow
        scrolled_window.add_with_viewport(img)

        # Add the scrolledwindow to the window
        self.add(scrolled_window)

win = Large_Image_Window()
win.show_all()

fetch_greenhouse_data()

win = DialogWindow()
win.show_all()

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

