#!/usr/bin/env python
# encoding: utf-8

# greenhouse.py
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

# linear actuator status filename
actuator_status_file_name = '/home/pi/Greenhouse/actuator.txt'
# solenoid valve status filename
solenoid_status_file_name = '/home/pi/Greenhouse/solenoid.txt'
# outputs status filename
outputs_status_file_name = '/home/pi/Greenhouse/outputs.txt'

# luminosity graph image local output file name
graph_image_luminosity = "/var/www/html/ghouselumi.png"
# temperature graph image local output file name
graph_image_temperature = "/var/www/html/ghousetemp.png"
# humidity graph image local output file name
graph_image_humidity = "/var/www/html/ghousehumi.png"
# soil moisture graph image local output file name
graph_image_soil_moisture = "/var/www/html/ghousesoil.png"

# luminosity graph image web/url file name
graph_image_luminosity_url = "/ghouselumi.png"
# temperature graph image web/url file name
graph_image_temperature_url = "/ghousetemp.png"
# humidity graph image web/url file name
graph_image_humidity_url = "/ghousehumi.png"
# soil moisture graph image web/url file name
graph_image_soil_moisture_url = "/ghousesoil.png"

# sqlite database file name
sqlite_database_file_name = '/var/www/html/greenhouse.db'

# static webpage file name
static_web_page_file_name = "/var/www/html/index.html"

# comma separated value output local file name
log_data_csv_file_name = "/var/www/html/index.csv"

# comma separated value web/url file name
log_data_csv_file_name_url = "index.csv"

# define the 16x2 RGB LCD device name connect via USB serial backpack kit
serial_lcd_device_name = '/dev/ttyACM0'

# define the length of time in seconds to display each message on the LCD screen
display_lcd_message_length = .9

# messages broadcast via the wall command are suffixed with this string
wall_terminal_message_suffix_string = "Ay-yahs.Greenhouse.Garden.Area.One"

# string dispalyed in the header of the html output
webpage_header_value = "Ay-yah's Greenhouse Automation System"

# define the model tempature sensor
# temp_sensor_model = Adafruit_DHT.AM2302
# temp_sensor_model = Adafruit_DHT.DHT11
temp_sensor_model = Adafruit_DHT.DHT22

# define which GPIO data pin number the sensors DATA pin two is connected on
temp_sensor_gpio = 25

# this actuators stroke is 406.4 mm at 10 mm per second
# wait 40.6 seconds to open the window
# in reality variations in voltage change the runtime
LINEAR_ACTUATOR_RUN_TIME = 70

# set the minimum value at 0.05VDC
MINIMUM_SOIL_MOISTURE_SENSOR_VALUE = 1

# set the minimum luminosity sensors value at 0.01VDC
MINIMUM_LUMINOSITY_SENSOR_VALUE = 0.01

# minimum light and temp and humidity values relay #2 close the window
MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT = 1.5
MINIMUM_TEMPERATURE_ACTUATOR_RETRACT = 80
MINIMUM_HUMIDITY_ACTUATOR_RETRACT = 90

# minimum light and temp and humidity values relay #1 open the window
MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND = 1.6
MINIMUM_TEMPERATURE_ACTUATOR_EXTEND = 50
MINIMUM_HUMIDITY_ACTUATOR_EXTEND = 20

# minimum temp or humidity values output #1 turn on the fan
MINIMUM_TEMPERATURE_OUTPUT_ONE_ON = 69
MINIMUM_HUMIDITY_OUTPUT_ONE_ON = 25

# minimum temp or humidity values output #1 turn off the fan
MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF = 50
MINIMUM_HUMIDITY_OUTPUT_ONE_OFF = 24

# minimum temp value output #2 turn on the USB heating pad
MINIMUM_TEMPERATURE_OUTPUT_TWO_ON = 35

# minimum temp value output #2 turn off the USB heating pad
MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF = 40

# minimum soil moisture value relay #3 open solenoid valve
MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN = 1.9

# minimum soil moisture value relay #3 close solenoid valve
MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED = 1.8

# define the minimum and maximum humidity/temperature sensor values
# minimum humidity value
MIMIMUM_HUMIDITY_VALUE = 0

# maximum humidity value
MAXIMUM_HUMIDITY_VALUE = 100

# minimum temperature value
MINIMUM_TEMPERATURE_VALUE = -72

# maximum temperature value
MAXIMUM_TEMPERATURE_VALUE = 176

##################################################################
#################### End Customizable Values #####################
##################################################################


##################################################################
################## Begin Subroutine Defintions ###################
##################################################################

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
            current_humidity, current_temperature = Adafruit_DHT.read_retry(
                temp_sensor_model, temp_sensor_gpio)

            print(current_humidity)
            print(current_temperature)

            if (current_temperature is not None and
                current_humidity is not None
                 ):
                # convert from a string to a floating-point number to an interger
                int(float(current_temperature))
                # convert from celsius to fahrenheit
                current_temperature = (current_temperature * 1.8) + 32
                # reformat as two decimals
                current_temperature = float("{0:.2f}".format(current_temperature))
                # reformat as two decimals
                current_humidity = float("{0:.2f}".format(current_humidity))

            if (current_humidity < MIMIMUM_HUMIDITY_VALUE):
                print(
                    'DHT sensor error humidity value less than minimum humidity value = %.2f Attempting reread' % current_humidity)

            if (current_humidity > MAXIMUM_HUMIDITY_VALUE):
                print(
                    'DHT sensor error humidity value greater than  = %.2f Attempting reread' % current_humidity)

            if (current_temperature < MINIMUM_TEMPERATURE_VALUE):
                print(
                    'DHT sensor error temperature value less than minimum temperature value = %.2f Attempting reread' % current_humidity)

            if (current_temperature > MAXIMUM_TEMPERATURE_VALUE):
                print(
                    'DHT sensor error temperature value greater than maximum temperature value = %.2f Attempting reread' % current_humidity)

            if (current_humidity > MIMIMUM_HUMIDITY_VALUE and current_humidity < MAXIMUM_HUMIDITY_VALUE and
                current_temperature > MINIMUM_TEMPERATURE_VALUE and current_temperature < MAXIMUM_TEMPERATURE_VALUE
                 ):
                return(current_humidity, current_temperature)
                break

        except RuntimeError as e:
            # print an error if the sensor read fails
            print("DHT sensor read failed: ", e.args)


# enable and disable outputs subroutine
# output #1 = 0, #2 = 1, #3 = 2
def control_outputs(output_number, output_status):

    outputs_status_file_handle = open(outputs_status_file_name, 'r')
    current_output_status_list = outputs_status_file_handle.readlines()
    outputs_status_file_handle.close()
    current_output_status = current_output_status_list[output_number]
    # remove the \n new line char from the end of the line
    current_output_status_list[output_number] = current_output_status_list[output_number].strip(
        '\n')

    if (current_output_status_list[output_number] == output_status):
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
            current_output_status_list[output_number] = "On\n"
            # write the modified status to a text file
            outputs_status_file_handle = open(outputs_status_file_name, 'w')
            outputs_status_file_handle.writelines(current_output_status_list)
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
            current_output_status_list[output_number] = "Off\n"
            # write the modified status to a text file
            outputs_status_file_handle = open(outputs_status_file_name, 'w')
            outputs_status_file_handle.writelines(current_output_status_list)
            outputs_status_file_handle.close()
            return(current_output_status)


# linear actuator extension and retraction subroutine
def linear_actuator_extension_retraction(actuator_extension_status):

    actuator_status_file_handle = open(actuator_status_file_name, 'r')
    current_actuator_extension_status = actuator_status_file_handle.readline()
    actuator_status_file_handle.close()

    if (current_actuator_extension_status == actuator_extension_status):
        return(current_actuator_extension_status)

    else:

        if (actuator_extension_status == 'Extended'):
            # toggle relay #2 on to extend the linear actuator
            automationhat.relay.one.toggle()
            time.sleep(LINEAR_ACTUATOR_RUN_TIME)

            # toggle relay #2 off
            automationhat.relay.one.toggle()
            current_actuator_extension_status = 'Extended'

            # write the modified status to a text file
            actuator_status_file_handle = open(actuator_status_file_name, 'w')
            actuator_status_file_handle.write(current_actuator_extension_status)
            actuator_status_file_handle.close()
            return(current_actuator_extension_status)

        if (actuator_extension_status == 'Retracted'):

            # toggle relay #1 on to retract the linear actuator
            automationhat.relay.two.toggle()
            time.sleep(LINEAR_ACTUATOR_RUN_TIME)

            # toggle relay #1 off
            automationhat.relay.two.toggle()
            current_actuator_extension_status = 'Retracted'
            # write the modified status to a text file
            actuator_status_file_handle = open(actuator_status_file_name, 'w')
            actuator_status_file_handle.write(current_actuator_extension_status)
            actuator_status_file_handle.close()
            return(current_actuator_extension_status)


# solenoid valve open and close subroutine
def solenoid_valve_operation(solenoid_valve_status):

    solenoid_status_file_handle = open(solenoid_status_file_name, 'r')
    current_solenoid_valve_status = solenoid_status_file_handle.readline()
    solenoid_status_file_handle.close()

    if (current_solenoid_valve_status == solenoid_valve_status):
        return(current_solenoid_valve_status)

    else:

        if (solenoid_valve_status == 'Open'):
            # toggle relay #3 on to open the solenoid valve
            pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 1"]
            p = subprocess.Popen(pigs_gpio_command_line)
            current_solenoid_valve_status = 'Open'

            # write the modified status to a text file
            solenoid_status_file_handle = open(solenoid_status_file_name, 'w')
            solenoid_status_file_handle.write(current_solenoid_valve_status)
            solenoid_status_file_handle.close()
            return(current_solenoid_valve_status)

        if (solenoid_valve_status == 'Closed'):
            # toggle relay #3 off to close the solenoid valve
            pigs_gpio_command_line = ["/usr/bin/pigs", "w 16 0"]
            p = subprocess.Popen(pigs_gpio_command_line)
            current_solenoid_valve_status = 'Closed'
            # write the modified status to a text file
            solenoid_status_file_handle = open(solenoid_status_file_name, 'w')
            solenoid_status_file_handle.write(current_solenoid_valve_status)
            solenoid_status_file_handle.close()
            return(current_solenoid_valve_status)


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
                print('ADC error read soil moisture value less than 0.05VDC = %.2f Attempting reread' %
                      current_soil_moisture_sensor_value)

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
                print('ADC error read LDR value less than 0.01VDC = %.3f Attempting reread' %
                      current_luminosity_sensor_value)

            if (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE):
                return(current_luminosity_sensor_value)
                break

        except RuntimeError as e:
            # print an error if the sensor read fails
            print("ADC sensor read failed: ", e.args)


# write text data to the 16x2 LCD subroutine as a serial device subroutine
def write_lcd_messages(write_lcd_message_content):

    ser = serial.Serial(serial_lcd_device_name, 9600, timeout=1)
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
    time.sleep(display_lcd_message_length)
    ser.write("%c%c" % (0xfe, 0x58))


# send console broadcast messages via wall
def write_wall_messages(write_wall_message_content):

    wall_message_text = '%s' % write_wall_message_content
    wall_message_text = wall_message_text + ' @' + wall_terminal_message_suffix_string
    # the wall applications -n no banner
    # option requires root thus sudo
    wall_message_command_line = ['sudo', 'wall', '-n', wall_message_text]

    # comment out the following line to disable console notifications
    p = subprocess.Popen(wall_message_command_line)


# write CSV output file subroutine
def write_csv_output_file(current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value, current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list):

    # begin file append of CSV file to the web server root
    # "Luminosity","Temperature","Humidity","Moisture",
    # "Solenoid","Actuator","Output1","Output2","Output3","Epoch"

    csv_file_handle = open(log_data_csv_file_name, "a")

    csv_file_handle.write('"')
    csv_file_handle.write(str(current_luminosity_sensor_value))
    csv_file_handle.write('",\"')

    csv_file_handle.write('')
    csv_file_handle.write(str(current_temperature))
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write(str(current_humidity))
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write(str(current_soil_moisture_sensor_value))
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write(current_solenoid_valve_status)
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write(current_actuator_extension_status)
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write('%s' % current_output_status_list[0])
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write('%s' % current_output_status_list[1])
    csv_file_handle.write('","')

    csv_file_handle.write('')
    csv_file_handle.write('%s' % current_output_status_list[2])
    csv_file_handle.write('","')

    # second since the epoch
    csv_file_handle.write('')
    csv_file_handle.write('%s' % time.time())
    csv_file_handle.write('"' + '\n')
    csv_file_handle.write('')
    csv_file_handle.close


# write sqlite database subroutine
def write_database_output(current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value, current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list):
    # begin file table data insert of row
    try:
        # establish a connection to the database
        connection_sqlite_database = sqlite3.connect(sqlite_database_file_name)
        curs = connection_sqlite_database.cursor()

        # insert data rows into the table
        curs.execute("INSERT INTO greenhouse (luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime) VALUES((?), (?), (?), (?), (?), (?), (?), (?), (?), date('now'), time('now'))",
                     (current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value,  current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list[0], current_output_status_list[1], current_output_status_list[2]))
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
        connection_sqlite_database = sqlite3.connect(sqlite_database_file_name)
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
        plt.savefig(graph_image_luminosity)

        plt.figure(1)
        plt.plot(date_values_no_year, values_temperature, '-')
        plt.show(block=True)
        plt.savefig(graph_image_temperature)

        plt.figure(2)
        plt.plot(date_values_no_year, values_humidity, '-')
        plt.show(block=True)
        plt.savefig(graph_image_humidity)

        plt.figure(3)
        plt.plot(date_values_no_year, values_soil_moisture, '-')
        plt.show(block=True)
        plt.savefig(graph_image_soil_moisture)

        # commit the changes
        connection_sqlite_database.commit()
        curs.close
        connection_sqlite_database.close()

    except sqlite3.IntegrityError as e:
        print('Sqlite Error: ', e.args[0])  # error output


# write static HTML file subroutine
def write_static_html_file(current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value, current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list, LINEAR_ACTUATOR_RUN_TIME, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE, webpage_header_value, MINIMUM_LUMINOSITY_SENSOR_VALUE, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT, MINIMUM_TEMPERATURE_ACTUATOR_RETRACT, MINIMUM_HUMIDITY_ACTUATOR_RETRACT, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_ACTUATOR_EXTEND, MINIMUM_HUMIDITY_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_OUTPUT_ONE_ON, MINIMUM_HUMIDITY_OUTPUT_ONE_ON, MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF, MINIMUM_HUMIDITY_OUTPUT_ONE_OFF, MINIMUM_TEMPERATURE_OUTPUT_TWO_ON, MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED):
    # begin file write of static HTML file to the web server root
    static_html_file_handle = open(static_web_page_file_name, "w")

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
    static_html_file_handle.write(webpage_header_value)
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
    static_html_file_handle.write(graph_image_luminosity_url)
    static_html_file_handle.write('">')
    static_html_file_handle.write('<img src="')
    static_html_file_handle.write(graph_image_luminosity_url)
    static_html_file_handle.write(
        '" alt="Greenhouse Luminosity Last 1000 Data Points" height="240" width="320"></a><br><center>')
    static_html_file_handle.write(current_luminosity_sensor_value)
    static_html_file_handle.write('VDC</center></td></tr>')

    current_temperature = str(current_temperature)
    static_html_file_handle.write('<tr><td>Temperature</td><td>')
    static_html_file_handle.write('<a href="')
    static_html_file_handle.write(graph_image_temperature_url)
    static_html_file_handle.write('">')
    static_html_file_handle.write('<img src="')
    static_html_file_handle.write(graph_image_temperature_url)
    static_html_file_handle.write(
        '" alt="Greenhouse Temperature Last 1000 Data Points" height="240" width="320"></a><br><center>')
    static_html_file_handle.write(current_temperature)
    static_html_file_handle.write('F</center></td></tr>')

    current_humidity = str(current_humidity)
    static_html_file_handle.write('<tr><td>Humidity</td><td>')
    static_html_file_handle.write('<a href="')
    static_html_file_handle.write(graph_image_humidity_url)
    static_html_file_handle.write('">')
    static_html_file_handle.write('<img src="')
    static_html_file_handle.write(graph_image_humidity_url)
    static_html_file_handle.write(
        '" alt="Greenhouse Humidity Last 1000 Data Points" height="240" width="320"></a><br><center>')
    static_html_file_handle.write(current_humidity)
    static_html_file_handle.write('%</center></td></tr>')

    current_soil_moisture_sensor_value = str(current_soil_moisture_sensor_value)
    static_html_file_handle.write('<tr><td>Soil moisture</td><td>')
    static_html_file_handle.write('<a href="')
    static_html_file_handle.write(graph_image_soil_moisture_url)
    static_html_file_handle.write('">')
    static_html_file_handle.write('<img src="')
    static_html_file_handle.write(graph_image_soil_moisture_url)
    static_html_file_handle.write(
        '" alt="Greenhouse Soil Moisture Last 1000 Data Points" height="240" width="320"></a><br><center>')
    static_html_file_handle.write(current_soil_moisture_sensor_value)
    static_html_file_handle.write('VDC</center></td></tr>')

    static_html_file_handle.write('<tr><td>Solenoid value</td><td>')
    static_html_file_handle.write(current_solenoid_valve_status)
    static_html_file_handle.write('</td></tr>')

    static_html_file_handle.write('<tr><td>Linear actuator</td><td>')
    static_html_file_handle.write(current_actuator_extension_status)
    static_html_file_handle.write('</td></tr>')

    static_html_file_handle.write(
        '<tr><td>Output #1 status (fan)</td><td> %s </td></tr>' % current_output_status_list[0])
    static_html_file_handle.write('<br>')
    static_html_file_handle.write(
        '<tr><td>Output #2 status (heat pad)</td><td> %s </td></tr>' % current_output_status_list[1])
    static_html_file_handle.write('<br>')
    static_html_file_handle.write('<tr><td>Output #3 status</td><td> %s </td></tr>' %
                                  current_output_status_list[2])
    static_html_file_handle.write('</table>')

    static_html_file_handle.write('<br><br><table>')
    static_html_file_handle.write('<tr><td>CSV data file</td><td>')
    static_html_file_handle.write('<a href="/')
    static_html_file_handle.write(log_data_csv_file_name_url)
    static_html_file_handle.write('">')
    static_html_file_handle.write(log_data_csv_file_name_url)
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

    MINIMUM_SOIL_MOISTURE_SENSOR_VALUE = str(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE)
    static_html_file_handle.write(
        '<tr><td>MINIMUM_SOIL_MOISTURE_SENSOR_VALUE</td><td>')
    static_html_file_handle.write(MINIMUM_SOIL_MOISTURE_SENSOR_VALUE)
    static_html_file_handle.write('VDC</td></tr>')

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

##################################################################
################### End Subroutine Defintions ####################
##################################################################


##################################################################
###### Begin Reading Input Write LCD Broadcast Wall Message ######
##################################################################
# begin the process reading evaluating environmental data
# display the current information on the 16x2 LCD and in
# the console window via wall messages
# call the read luminosity sensor value subroutine
current_luminosity_sensor_value = read_luminosity_sensor_value()
# display the luminosity value on the LCD
current_luminosity_sensor_value
write_lcd_message_content = 'Luminosity: %s' % current_luminosity_sensor_value
write_lcd_messages(write_lcd_message_content)
# display the luminosity value via a console broadcast message
write_wall_message_content = 'Luminosity: %s' % current_luminosity_sensor_value
write_wall_messages(write_wall_message_content)

# call our read temperature and humidity value subroutine
current_humidity, current_temperature = read_temperature_humidity_values()
# display the temperature value on the LCD
write_lcd_message_content = 'Temp: %s' % current_temperature
write_lcd_messages(write_lcd_message_content)
# display the temperature value via a console broadcast message
write_wall_message_content = 'Temp: %s' % current_temperature
write_wall_messages(write_wall_message_content)

# display the humidity value on the LCD
write_lcd_message_content = 'Humidity: %s' % current_humidity
write_lcd_messages(write_lcd_message_content)
# display the humidity value via a console broadcast message
write_wall_message_content = 'Humidity: %s' % current_humidity
write_wall_messages(write_wall_message_content)

# call the read soil moisture sensor value subroutine
current_soil_moisture_sensor_value = read_soil_moisture_sensor_value()
# display soil moisture sensor on the LCD
write_lcd_message_content = 'Soil moisture: %s' % current_soil_moisture_sensor_value
write_lcd_messages(write_lcd_message_content)
# display the soil moisture value via a console broadcast message
write_wall_message_content = 'Soil moisture: %s' % current_soil_moisture_sensor_value
write_wall_messages(write_wall_message_content)

# read the current solenoid valve status
solenoid_status_file_handle = open(solenoid_status_file_name, 'r')
current_solenoid_valve_status = solenoid_status_file_handle.readline()
solenoid_status_file_handle.close()
# display the solenoid value status on the LCD
write_lcd_message_content = 'Solenoid: %s' % current_solenoid_valve_status
write_lcd_messages(write_lcd_message_content)
# display the solenoid value status via a console broadcast message
write_wall_message_content = 'Solenoid: %s' % current_solenoid_valve_status
write_wall_messages(write_wall_message_content)

# read the current linear actuator status
actuator_status_file_handle = open(actuator_status_file_name, 'r')
current_actuator_extension_status = actuator_status_file_handle.readline()
actuator_status_file_handle.close()
# display the linear actuator status on the LCD
write_lcd_message_content = 'Linear actuator: %s' % current_actuator_extension_status
write_lcd_messages(write_lcd_message_content)
# display the linear actuator status via a console broadcast message
write_wall_message_content = 'Linear actuator: %s' % current_actuator_extension_status
write_wall_messages(write_wall_message_content)

# display the outputs status values via a console broadcast messages
outputs_status_file_handle = open(outputs_status_file_name, 'r')
current_output_status_list = outputs_status_file_handle.readlines()
outputs_status_file_handle.close()
# remove the \n new line char from the end of the line
current_output_status_list[0] = current_output_status_list[0].strip('\n')
current_output_status_list[1] = current_output_status_list[1].strip('\n')
current_output_status_list[2] = current_output_status_list[2].strip('\n')
# display the outputs status on the LCD
write_lcd_message_content = 'Output #1 status: %s' % current_output_status_list[0]
write_lcd_messages(write_lcd_message_content)
write_lcd_message_content = 'Output #2 status: %s' % current_output_status_list[1]
write_lcd_messages(write_lcd_message_content)
write_lcd_message_content = 'Output #3 status: %s' % current_output_status_list[2]
write_lcd_messages(write_lcd_message_content)
# display the outputs status via a console broadcast message
write_wall_message_content = 'Output #1 status: %s' % current_output_status_list[0]
write_wall_messages(write_wall_message_content)
write_wall_message_content = 'Output #2 status: %s' % current_output_status_list[1]
write_wall_messages(write_wall_message_content)
write_wall_message_content = 'Output #3 status: %s' % current_output_status_list[2]
write_wall_messages(write_wall_message_content)

##################################################################
##### End Reading Input Writing LCD Broadcasting Wall Message ####
##################################################################


##################################################################
#################### Begin Evaluation Process ####################
##################################################################
# begin the process of evaluating environmental conditions and
# respond accordingly

# evaulate if we close or open the window
if (current_luminosity_sensor_value <= MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT and
    current_temperature <= MINIMUM_TEMPERATURE_ACTUATOR_RETRACT and
    current_humidity <= MINIMUM_HUMIDITY_ACTUATOR_RETRACT and
    current_solenoid_valve_status == 'Closed'
     ):
    # retract the linear actuator and close the window
    actuator_extension_status = 'Retracted'
    current_actuator_extension_status = linear_actuator_extension_retraction(
        actuator_extension_status)

elif (current_luminosity_sensor_value > MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND and
      current_temperature > MINIMUM_TEMPERATURE_ACTUATOR_EXTEND and
      current_humidity > MINIMUM_HUMIDITY_ACTUATOR_EXTEND and
      current_solenoid_valve_status == 'Closed'
      ):
    # extend the linear actuator and open the window
    actuator_extension_status = 'Extended'
    current_actuator_extension_status = linear_actuator_extension_retraction(
        actuator_extension_status)

# evaulate if we need to enable output #1 turn on the fan
if (current_temperature >= MINIMUM_TEMPERATURE_OUTPUT_ONE_ON or
    current_humidity >= MINIMUM_HUMIDITY_OUTPUT_ONE_ON and
    current_solenoid_valve_status == 'Closed'
     ):
    # enable output one
    output_number = 0
    output_status = 'On'
    current_output_status = control_outputs(output_number, output_status)

elif (current_temperature < MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF or
      current_humidity < MINIMUM_HUMIDITY_OUTPUT_ONE_OFF
      ):
    # disable output one
    output_number = 0
    output_status = 'Off'
    current_output_status = control_outputs(output_number, output_status)

# evaulate if we need to enable output #2 turn on the USB heating pad
if (current_temperature <= MINIMUM_TEMPERATURE_OUTPUT_TWO_ON
      ):
    # enable output two
    output_number = 1
    output_status = 'On'
    current_output_status = control_outputs(output_number, output_status)

elif (current_temperature > MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF
      ):
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

##################################################################
##################### End Evaluation Process #####################
##################################################################


##################################################################
###### Begin HTML, Database, CSV, Graph Image Update Process #####
##################################################################


# call the write static HTML output file subroutine
write_static_html_file(current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value, current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list, LINEAR_ACTUATOR_RUN_TIME, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE, webpage_header_value, MINIMUM_LUMINOSITY_SENSOR_VALUE, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_RETRACT, MINIMUM_TEMPERATURE_ACTUATOR_RETRACT,
                    MINIMUM_HUMIDITY_ACTUATOR_RETRACT, MINIMUM_LUMINOSITY_SENSOR_VALUE_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_ACTUATOR_EXTEND, MINIMUM_HUMIDITY_ACTUATOR_EXTEND, MINIMUM_TEMPERATURE_OUTPUT_ONE_ON, MINIMUM_HUMIDITY_OUTPUT_ONE_ON, MINIMUM_TEMPERATURE_OUTPUT_ONE_OFF, MINIMUM_HUMIDITY_OUTPUT_ONE_OFF, MINIMUM_TEMPERATURE_OUTPUT_TWO_ON, MINIMUM_TEMPERATURE_OUTPUT_TWO_OFF, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_OPEN, MINIMUM_SOIL_MOISTURE_SENSOR_VALUE_SOLENOID_CLOSED)

# call the write database table subroutine
write_database_output(current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value,
                    current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list)

# call the write CSV output file subroutine
write_csv_output_file(current_luminosity_sensor_value, current_temperature, current_humidity, current_soil_moisture_sensor_value,
                   current_solenoid_valve_status, current_actuator_extension_status, current_output_status_list)

# call the read database table data output graph files subroutine
read_database_output_graphs()

##################################################################
####### End HTML, Database, CSV, Graph Image Update Process ######
##################################################################
