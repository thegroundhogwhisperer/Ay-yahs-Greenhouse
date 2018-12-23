#!/usr/bin/env python
# encoding: utf-8

# greenhouse.py
# Copyright (C) 2018 The Groundhog Whisperer
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
# control and irrigation in a small greenhouse. Climate control and
# irrigation control is achieved by monitoring environmental sensor
# measurements. The environmental sensors measurements are then used to
# control a linear actuator, solenoid valve, small fan, and small heating
# pad. The information produced is displayed on a 16x2 LCD screen,
# broadcast via a wall message to the console, written to an HTML file,
# and written to a CSV file.

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
plt.use('Agg') # initilized because it needs a different backend for the display to not crash when executed from the console
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use('fivethirtyeight') # select the style of graph
from dateutil import parser


##################################################################
###################### Customizable Values #######################
##################################################################

# linear actuator status filename
actuatorStatusFileName = '/home/pi/Greenhouse/actuator.txt'
# solenoid valve status filename
solenoidStatusFileName = '/home/pi/Greenhouse/solenoid.txt'
# outputs status filename
outputsStatusFileName = '/home/pi/Greenhouse/outputs.txt'

# luminosity graph image local output file name
graphImageLuminosity = "/var/www/html/ghouselumi.png"
# temperature graph image local output file name
graphImageTemperature = "/var/www/html/ghousetemp.png"
# humidity graph image local output file name
graphImageHumidity = "/var/www/html/ghousehumi.png"
# soil moisture graph image local output file name
graphImageSoilMoisture = "/var/www/html/ghousesoil.png"

# luminosity graph image web/url file name
graphImageLuminosityURL = "/ghouselumi.png"
# temperature graph image web/url file name
graphImageTemperatureURL = "/ghousetemp.png"
# humidity graph image web/url file name
graphImageHumidityURL = "/ghousehumi.png"
# soil moisture graph image web/url file name
graphImageSoilMoistureURL = "/ghousesoil.png"

# sqlite database file name
sqliteDatabaseFileName = '/var/www/html/greenhouse.db'

# static webpage file name
staticWebPageFileName = "/var/www/html/index.html"

# CSV output local file name
logDataCSVFileName = "/var/www/html/index.csv"

# CSV web/url file name
logDataCSVFileNameURL = "index.csv"

# this actuators stroke is 406.4 mm at 10 mm per second
# wait 40.6 seconds to open the window
linearActuatorRunTime = 70

# set the minimum value at 0.05VDC
minimumSoilMoistureSensorValue = 1

# set the minimum luminosity sensors value at 0.01VDC
minimumLuminositySensorValue = 0.01

# define the 16x2 RGB LCD device name connect via USB serial backpack kit
serialLCDDeviceName = '/dev/ttyACM0'

# define the length of time in seconds to display each message on the LCD screen
displayLCDMessageLength = .9

wallMessagePrefixString = "Ay-yahs.Greenhouse.Garden.Area.One"

webpageHeaderValue = "Ay-yah's Greenhouse Automation System"

# minimum light and temp and humidity values relay #2 close the window
minimumLuminositySensorValueActuatorRetract = 1.5
minimumTemperatureActuatorRetract = 80
minimumHumidityActuatorRetract = 90

# minimum light and temp and humidity values relay #1 open the window
minimumLuminositySensorValueActuatorExtend = 1.6
minimumTemperatureActuatorExtend = 50
minimumHumidityActuatorExtend = 20

# minimum temp or humidity values output #1 turn on the fan
minimumTemperatureOutputOneOn = 69
minimumHumidityOutputOneOn = 25

# minimum temp or humidity values output #1 turn off the fan
minimumTemperatureOutputOneOff = 50
minimumHumidityOutputOneOff = 24

# minimum temp value output #2 turn on the USB heating pad
minimumTemperatureOutputTwoOn = 35

# minimum temp value output #2 turn off the USB heating pad
minimumTemperatureOutputTwoOff = 40

# minimum soil moisture value relay #3 open solenoid valve
minimumSoilMoistureSensorValueSolenoidOpen = 1.9

# minimum soil moisture value relay #3 close solenoid valve
minimumSoilMoistureSensorValueSolenoidClosed = 1.8

##################################################################
#################### End Customizable Values #####################
##################################################################


##################################################################
################## Begin Subroutine Defintions ###################
##################################################################

# temperature and humidity value read input subroutine
def readTemperatureHumidityValues():

    # define the model tempature sensor
    #tempSensorModel = Adafruit_DHT.DHT11
    tempSensorModel = Adafruit_DHT.DHT22
    #tempSensorModel = Adafruit_DHT.AM2302
    # define the data pin number
    tempSensorGPIO = 25

    # the sensor may produce an erroneous humidity reading greater than 100%
    # a for loop retrys the read process until a value < 100% is returned
    for i in range(0, 10):
        try:

            # create an instance of the dht22 class
            # pass the GPIO data pin number connected to the signal line
            # (pin #25 is broken out on the Pimoroni Automation HAT)
            # read the temperature and humidity values
            currentHumidity, currentTemperature = Adafruit_DHT.read_retry(
                tempSensorModel, tempSensorGPIO)

            # convert from a string to a floating-point number to an interger
            int(float(currentTemperature))
            # convert from celsius to fahrenheit
            currentTemperature = (currentTemperature * 1.8) + 32
            # reformat as two decimals
            currentTemperature = float("{0:.2f}".format(currentTemperature))
            # reformat as two decimals
            currentHumidity = float("{0:.2f}".format(currentHumidity))

            # set the maximum humidity value at 100%
            impossibleHumidity = 100
            if (currentHumidity > impossibleHumidity):
                print(
                    'DHT sensor error humidity value greater than 100 = %.2f Attempting reread' % currentHumidity)

            if (currentHumidity < impossibleHumidity):
                return(currentHumidity, currentTemperature)
                break

        except RuntimeError as e:
            # print an error if the sensor read fails
            print("DHT sensor read failed: ", e.args)


# enable and disable outputs subroutine
# output #1 = 0, #2 = 1, #3 = 2
def controlOutputs(outputNumber, outputStatus):

    outputsStatusFileHandle = open(outputsStatusFileName, 'r')
    currentOutputStatusList = outputsStatusFileHandle.readlines()
    outputsStatusFileHandle.close()
    currentOutputStatus = currentOutputStatusList[outputNumber]
    # remove the \n new line char from the end of the line
    currentOutputStatusList[outputNumber] = currentOutputStatusList[outputNumber].strip(
        '\n')

    if (currentOutputStatusList[outputNumber] == outputStatus):
        return(currentOutputStatus)

    else:

        if (outputStatus == 'On'):
            # toggle output on
            if (outputNumber == 0):
                pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 1"]
                p = subprocess.Popen(pigsGPIOCommandLine)

            elif (outputNumber == 1):
                pigsGPIOCommandLine = ["/usr/bin/pigs", "w 12 1"]
                p = subprocess.Popen(pigsGPIOCommandLine)

            elif (outputNumber == 2):
                pigsGPIOCommandLine = ["/usr/bin/pigs", "w 6 1"]
                p = subprocess.Popen(pigsGPIOCommandLine)

            currentOutputStatus = 'On'
            currentOutputStatusList[outputNumber] = "On\n"
            # write the modified status to a text file
            outputsStatusFileHandle = open(outputsStatusFileName, 'w')
            outputsStatusFileHandle.writelines(currentOutputStatusList)
            outputsStatusFileHandle.close()
            return(currentOutputStatus)

        if (outputStatus == 'Off'):
            # toggle output off
            if (outputNumber == 0):
                pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 0"]
                p = subprocess.Popen(pigsGPIOCommandLine)

            elif (outputNumber == 1):
                pigsGPIOCommandLine = ["/usr/bin/pigs", "w 12 0"]
                p = subprocess.Popen(pigsGPIOCommandLine)

            elif (outputNumber == 2):
                pigsGPIOCommandLine = ["/usr/bin/pigs", "w 6 0"]
                p = subprocess.Popen(pigsGPIOCommandLine)

            currentOutputStatus = 'Off'
            currentOutputStatusList[outputNumber] = "Off\n"
            # write the modified status to a text file
            outputsStatusFileHandle = open(outputsStatusFileName, 'w')
            outputsStatusFileHandle.writelines(currentOutputStatusList)
            outputsStatusFileHandle.close()
            return(currentOutputStatus)


# linear actuator extension and retraction subroutine
def linearActuatorExtensionRetraction(actuatorExtensionStatus):

    actuatorStatusFileHandle = open(actuatorStatusFileName, 'r')
    currentActuatorExtensionStatus = actuatorStatusFileHandle.readline()
    actuatorStatusFileHandle.close()

    if (currentActuatorExtensionStatus == actuatorExtensionStatus):
        return(currentActuatorExtensionStatus)

    else:

        if (actuatorExtensionStatus == 'Extended'):
            # toggle relay #2 on to extend the linear actuator
            automationhat.relay.one.toggle()
            time.sleep(linearActuatorRunTime)

            # toggle relay #2 off
            automationhat.relay.one.toggle()
            currentActuatorExtensionStatus = 'Extended'

            # write the modified status to a text file
            actuatorStatusFileHandle = open(actuatorStatusFileName, 'w')
            actuatorStatusFileHandle.write(currentActuatorExtensionStatus)
            actuatorStatusFileHandle.close()
            return(currentActuatorExtensionStatus)

        if (actuatorExtensionStatus == 'Retracted'):

            # toggle relay #1 on to retract the linear actuator
            automationhat.relay.two.toggle()
            time.sleep(linearActuatorRunTime)

            # toggle relay #1 off
            automationhat.relay.two.toggle()
            currentActuatorExtensionStatus = 'Retracted'
            # write the modified status to a text file
            actuatorStatusFileHandle = open(actuatorStatusFileName, 'w')
            actuatorStatusFileHandle.write(currentActuatorExtensionStatus)
            actuatorStatusFileHandle.close()
            return(currentActuatorExtensionStatus)


# solenoid valve open and close subroutine
def solenoidValveOperation(solenoidValveStatus):

    solenoidStatusFileHandle = open(solenoidStatusFileName, 'r')
    currentSolenoidValveStatus = solenoidStatusFileHandle.readline()
    solenoidStatusFileHandle.close()

    if (currentSolenoidValveStatus == solenoidValveStatus):
        return(currentSolenoidValveStatus)

    else:

        if (solenoidValveStatus == 'Open'):
            # toggle relay #3 on to open the solenoid valve
            pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 1"]
            p = subprocess.Popen(pigsGPIOCommandLine)
            currentSolenoidValveStatus = 'Open'

            # write the modified status to a text file
            solenoidStatusFileHandle = open(solenoidStatusFileName, 'w')
            solenoidStatusFileHandle.write(currentSolenoidValveStatus)
            solenoidStatusFileHandle.close()
            return(currentSolenoidValveStatus)

        if (solenoidValveStatus == 'Closed'):
            # toggle relay #3 off to close the solenoid valve
            pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 0"]
            p = subprocess.Popen(pigsGPIOCommandLine)
            currentSolenoidValveStatus = 'Closed'
            # write the modified status to a text file
            solenoidStatusFileHandle = open(solenoidStatusFileName, 'w')
            solenoidStatusFileHandle.write(currentSolenoidValveStatus)
            solenoidStatusFileHandle.close()
            return(currentSolenoidValveStatus)


# analog to digital converter #1 read soil moisture sensor value subroutine
def readSoilMoistureSensorValue():

    # the ADC may produce an erroneous moisture reading less than 0.05VDC
    # a for loop retrys the read process until a value > 0.05VDC is returned
    for i in range(0, 25):
        try:

            # initilized the counter variable
            readCounter = 0
            temporaryValue = float()
            temporaryValuesList = list()
            currentSoilMoistureSensorValue = float()
            standardDeviationOfSensorValues = 0

            # loop through multiple data reads
            while readCounter < 2:
                # read the moisture value from analog to
                # digital converter #1
                temporaryValue = automationhat.analog[0].read()
                # keep one of the values in case the read is
                # consistent
                goodTemporaryValue = temporaryValue
                time.sleep(.9)

                # populate a list of values
                temporaryValuesList.append(temporaryValue)
                readCounter = readCounter + 1

            # if the standard deviation of the series of
            # readings is zero then the sensor produced
            # multiple consistent values and we should
            # consider the data reliable and take actions

            # return the standard deviation of the list of values
            standardDeviationOfSensorValues = math.sqrt(
                statistics.pvariance(temporaryValuesList))
            # if there is no difference in the values
            # use the goodTemporaryValue they are all
            # the same
            if (standardDeviationOfSensorValues == 0):
                currentSoilMoistureSensorValue = goodTemporaryValue

            elif (standardDeviationOfSensorValues != 0):
                # if there is a difference set the value
                # to zero and try again for a consistent
                # data read
                currentSoilMoistureSensorValue = 0

            if (currentSoilMoistureSensorValue <= .09):
                print('ADC error read soil moisture value less than 0.05VDC = %.2f Attempting reread' %
                      currentSoilMoistureSensorValue)

            if (currentSoilMoistureSensorValue > minimumSoilMoistureSensorValue):
                return(currentSoilMoistureSensorValue)
                break

        except RuntimeError as e:
            # print an error if the sensor read fails
            print("ADC sensor read failed: ", e.args)


# analog to digital converter #2 read light dependent resistor value subroutine
def readLuminositySensorValue():

    # the ADC may produce an erroneous luminisoty reading less than 0.00VDC
    # a for loop retrys the read process until a value > 0.00VDC is returned
    for i in range(0, 25):
        try:

            # initilized the counter variable
            readCounter = 0
            temporaryValue = float()
            temporaryValuesList = list()
            currentLuminositySensorValue = float()
            standardDeviationOfSensorValues = 0

            # loop through multiple data reads
            while readCounter < 2:
                # read the light value from analog to digital converter #2
                temporaryValue = automationhat.analog[1].read()
                # keep one of the values in case the read is
                # consistent
                goodTemporaryValue = temporaryValue
                time.sleep(.9)

                # populate a list of values
                temporaryValuesList.append(temporaryValue)
                readCounter = readCounter + 1

            # If the standard deviation of the series of
            # readings is zero then the sensor produced
            # multiple consistent values and we should
            # consider the data reliable and take actions
            # return the standard deviation of the list of values
            standardDeviationOfSensorValues = math.sqrt(
                statistics.pvariance(temporaryValuesList))

            # if there is no difference in the values
            # use the goodTemporaryValue they are all
            # the same
            if (standardDeviationOfSensorValues == 0):
                currentLuminositySensorValue = goodTemporaryValue
            elif (standardDeviationOfSensorValues != 0):
                # if there is a difference set the value
                # to zero and try again for a consistent
                # data read
                currentLuminositySensorValue = 0

            if (currentLuminositySensorValue < 0.05):
                print('ADC error read LDR value less than 0.01VDC = %.3f Attempting reread' %
                      currentLuminositySensorValue)

            if (currentLuminositySensorValue > minimumLuminositySensorValue):
                return(currentLuminositySensorValue)
                break

        except RuntimeError as e:
            # print an error if the sensor read fails
            print("ADC sensor read failed: ", e.args)


# write text data to the 16x2 LCD subroutine as a serial device subroutine
def writeLCDMessages(writeLCDMessageContent):

    ser = serial.Serial(serialLCDDeviceName, 9600, timeout=1)
    # enable auto scrolling
    ser.write("%c%c" % (0xfe, 0x51))
    time.sleep(.1)

    # clear the screen
    ser.write("%c%c" % (0xfe, 0x58))
    time.sleep(.1)

    # change the lcd back light color
    #ser.write("%c%c%c%c%c" % (0xfe, 0xd0, 0x0, 0x0, 0xff))
    # time.sleep(.5)
    #ser.write("%c%c%c%c%c" % (0xfe, 0xd0, 0xff, 0xff, 0xff))
    # time.sleep(.5)

    ser.write(writeLCDMessageContent)
    time.sleep(displayLCDMessageLength)
    ser.write("%c%c" % (0xfe, 0x58))


# send console broadcast messages via wall
def writeWallMessages(writeWallMessageContent):

    wallMessageText = '%s' % writeWallMessageContent
    wallMessageText = wallMessageText + ' @' + wallMessagePrefixString
    # the wall applications -n no banner
    # option requires root thus sudo
    wallMessageCommandLine = ['sudo', 'wall', '-n', wallMessageText]

    # comment out the following line to disable console notifications
    p = subprocess.Popen(wallMessageCommandLine)


# write CSV output file subroutine
def writeCSVOutputFile(currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue, currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList):

    # begin file append of CSV file to the web server root
    # "Luminosity","Temperature","Humidity","Moisture",
    # "Solenoid","Actuator","Output1","Output2","Output3","Epoch"

    csvFileHandle = open(logDataCSVFileName, "a")

    csvFileHandle.write('"')
    csvFileHandle.write(str(currentLuminositySensorValue))
    csvFileHandle.write('",\"')

    csvFileHandle.write('')
    csvFileHandle.write(str(currentTemperature))
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write(str(currentHumidity))
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write(str(currentSoilMoistureSensorValue))
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write(currentSolenoidValveStatus)
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write(currentActuatorExtensionStatus)
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write('%s' % currentOutputStatusList[0])
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write('%s' % currentOutputStatusList[1])
    csvFileHandle.write('","')

    csvFileHandle.write('')
    csvFileHandle.write('%s' % currentOutputStatusList[2])
    csvFileHandle.write('","')

    # second since the epoch
    csvFileHandle.write('')
    csvFileHandle.write('%s' % time.time())
    csvFileHandle.write('"' + '\n')
    csvFileHandle.write('')
    csvFileHandle.close


# write sqlite database subroutine
def writeDatabaseOutput(currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue, currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList):
    # begin file table data insert of row
    try:
        # establish a connection to the database
        connectionSQLiteDatabase = sqlite3.connect(sqliteDatabaseFileName)
        curs = connectionSQLiteDatabase.cursor()

        # insert data rows into the table
        curs.execute("INSERT INTO greenhouse (luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime) VALUES((?), (?), (?), (?), (?), (?), (?), (?), (?), date('now'), time('now'))",
                     (currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue,  currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList[0], currentOutputStatusList[1], currentOutputStatusList[2]))
        # commit the changes
        connectionSQLiteDatabase.commit()
        curs.close
        connectionSQLiteDatabase.close()

    except sqlite3.IntegrityError as e:
        print('Sqlite Error: ', e.args[0])  # error output


# read sqlite database generate graphs subroutine
def readDatabaseOutputGraphs():
    # begin file append of CSV file to the web server root
    # read a sqlite database table and generate a graph

    try:
        # establish a connection to the database
        connectionSQLiteDatabase = sqlite3.connect(sqliteDatabaseFileName)
        curs = connectionSQLiteDatabase.cursor()

        # select data rows from the table
    # curs.execute("INSERT INTO greenhouse (luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime) VALUES((?), (?), (?), (?), (?), (?), (?), (?), (?), date('now'), time('now'))", (currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue,  currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList[0], currentOutputStatusList[1], currentOutputStatusList[2]))
        curs.execute('SELECT luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime FROM greenhouse ORDER BY ROWID DESC LIMIT 1000 ')
#        curs.execute('SELECT luminosity, temperature, humidity, soilmoisture, solenoidstatus, actuatorstatus, outputonestatus, outputtwostatus, outputthreestatus, currentdate, currenttime FROM greenhouse LIMIT 4000')
    #  curs.execute('SELECT temperature, currentdate FROM greenhouse LIMIT 2000')

        dataRowFetchedAll = curs.fetchall()
        dateValues = []
        dateValuesNoYear = []
        valuesLuminosity = []
        valuesTemperature = []
        valuesHumidity = []
        valuesSoilMoisture = []

        for row in dataRowFetchedAll:
            valuesLuminosity.append(row[0])
            valuesTemperature.append(row[1])
            valuesHumidity.append(row[2])
            valuesSoilMoisture.append(row[3])
            dateValues.append(parser.parse(row[9]))
            tempString = row[9].split("-", 1)
            dateValuesNoYear.append(tempString[1])

    #  plt.plot(dateValuesNoYear, valuesTemperature, '-')
        plt.figure(0)
        plt.plot(dateValuesNoYear, valuesLuminosity, '-')

    #  plt.plot(valuesLuminosity, dateValues)
        plt.show(block=True)
        plt.savefig(graphImageLuminosity)

        plt.figure(1)
        plt.plot(dateValuesNoYear, valuesTemperature, '-')
        plt.show(block=True)
        plt.savefig(graphImageTemperature)

        plt.figure(2)
        plt.plot(dateValuesNoYear, valuesHumidity, '-')
        plt.show(block=True)
        plt.savefig(graphImageHumidity)

        plt.figure(3)
        plt.plot(dateValuesNoYear, valuesSoilMoisture, '-')
        plt.show(block=True)
        plt.savefig(graphImageSoilMoisture)

        # commit the changes
        connectionSQLiteDatabase.commit()
        curs.close
        connectionSQLiteDatabase.close()

    except sqlite3.IntegrityError as e:
        print('Sqlite Error: ', e.args[0])  # error output


# write static HTML file subroutine
def writeStaticHTMLFile(currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue, currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList, linearActuatorRunTime, minimumSoilMoistureSensorValue, webpageHeaderValue, minimumLuminositySensorValue, minimumLuminositySensorValueActuatorRetract, minimumTemperatureActuatorRetract, minimumHumidityActuatorRetract, minimumLuminositySensorValueActuatorExtend, minimumTemperatureActuatorExtend, minimumHumidityActuatorExtend, minimumTemperatureOutputOneOn, minimumHumidityOutputOneOn, minimumTemperatureOutputOneOff, minimumHumidityOutputOneOff, minimumTemperatureOutputTwoOn, minimumTemperatureOutputTwoOff, minimumSoilMoistureSensorValueSolenoidOpen, minimumSoilMoistureSensorValueSolenoidClosed):
    # begin file write of static HTML file to the web server root
    staticWebPageFileHandle = open(staticWebPageFileName, "w")

    staticWebPageFileHandle.write("""
    <html>

    <head>
      <style>
       table, th, td{
        border: 1px solid #333;
       }
      </style>

    <meta http-equiv="refresh" content="600"0">

    <title>Greenhouse Automation System Status Information</title></head>

    <body bgcolor="#CCFFFF">
    """)

    staticWebPageFileHandle.write('<h3 align="center">')
    staticWebPageFileHandle.write(webpageHeaderValue)
    staticWebPageFileHandle.write('<br>Status Information</h3>')

    staticWebPageFileHandle.write(
        '<center><a href="/greenhousehigh.jpg"><img src="/greenhouselow.gif" alt="Greenhouse Camera Image - Animated GIF file"  height="240" width="320"><br>Click for high resolution</center></a>')
    staticWebPageFileHandle.write('<center><table>')
    staticWebPageFileHandle.write(
        '<caption>Current Environmental Data</caption>')
    staticWebPageFileHandle.write(
        '<tr><th>Reading Type</th><th>Value</th></tr>')

    currentLuminositySensorValue = str(currentLuminositySensorValue)
    staticWebPageFileHandle.write('<tr><td>')
    staticWebPageFileHandle.write('Luminosity</td><td>')
    staticWebPageFileHandle.write('<a href="')
    staticWebPageFileHandle.write(graphImageLuminosityURL)
    staticWebPageFileHandle.write('">')
    staticWebPageFileHandle.write('<img src="')
    staticWebPageFileHandle.write(graphImageLuminosityURL)
    staticWebPageFileHandle.write(
        '" alt="Greenhouse Luminosity Last 2000 Data Points" height="240" width="320"></a><br><center>')
    staticWebPageFileHandle.write(currentLuminositySensorValue)
    staticWebPageFileHandle.write('VDC</center></td></tr>')

    currentTemperature = str(currentTemperature)
    staticWebPageFileHandle.write('<tr><td>Temperature</td><td>')
    staticWebPageFileHandle.write('<a href="')
    staticWebPageFileHandle.write(graphImageTemperatureURL)
    staticWebPageFileHandle.write('">')
    staticWebPageFileHandle.write('<img src="')
    staticWebPageFileHandle.write(graphImageTemperatureURL)
    staticWebPageFileHandle.write(
        '" alt="Greenhouse Temperature Last 2000 Data Points" height="240" width="320"></a><br><center>')
    staticWebPageFileHandle.write(currentTemperature)
    staticWebPageFileHandle.write('F</center></td></tr>')

    currentHumidity = str(currentHumidity)
    staticWebPageFileHandle.write('<tr><td>Humidity</td><td>')
    staticWebPageFileHandle.write('<a href="')
    staticWebPageFileHandle.write(graphImageHumidityURL)
    staticWebPageFileHandle.write('">')
    staticWebPageFileHandle.write('<img src="')
    staticWebPageFileHandle.write(graphImageHumidityURL)
    staticWebPageFileHandle.write(
        '" alt="Greenhouse Humidity Last 2000 Data Points" height="240" width="320"></a><br><center>')
    staticWebPageFileHandle.write(currentHumidity)
    staticWebPageFileHandle.write('%</center></td></tr>')

    currentSoilMoistureSensorValue = str(currentSoilMoistureSensorValue)
    staticWebPageFileHandle.write('<tr><td>Soil moisture</td><td>')
    staticWebPageFileHandle.write('<a href="')
    staticWebPageFileHandle.write(graphImageSoilMoistureURL)
    staticWebPageFileHandle.write('">')
    staticWebPageFileHandle.write('<img src="')
    staticWebPageFileHandle.write(graphImageSoilMoistureURL)
    staticWebPageFileHandle.write(
        '" alt="Greenhouse Soil Moisture Last 2000 Data Points" height="240" width="320"></a><br><center>')
    staticWebPageFileHandle.write(currentSoilMoistureSensorValue)
    staticWebPageFileHandle.write('VDC</center></td></tr>')

    staticWebPageFileHandle.write('<tr><td>Solenoid value</td><td>')
    staticWebPageFileHandle.write(currentSolenoidValveStatus)
    staticWebPageFileHandle.write('</td></tr>')

    staticWebPageFileHandle.write('<tr><td>Linear actuator</td><td>')
    staticWebPageFileHandle.write(currentActuatorExtensionStatus)
    staticWebPageFileHandle.write('</td></tr>')

    staticWebPageFileHandle.write(
        '<tr><td>Output #1 status (fan)</td><td> %s </td></tr>' % currentOutputStatusList[0])
    staticWebPageFileHandle.write('<br>')
    staticWebPageFileHandle.write(
        '<tr><td>Output #2 status (heat pad)</td><td> %s </td></tr>' % currentOutputStatusList[1])
    staticWebPageFileHandle.write('<br>')
    staticWebPageFileHandle.write('<tr><td>Output #3 status</td><td> %s </td></tr>' %
                                  currentOutputStatusList[2])
    staticWebPageFileHandle.write('</table>')

    staticWebPageFileHandle.write('<br><br><table>')
    staticWebPageFileHandle.write('<tr><td>CSV data file</td><td>')
    staticWebPageFileHandle.write('<a href="/')
    staticWebPageFileHandle.write(logDataCSVFileNameURL)
    staticWebPageFileHandle.write('">')
    staticWebPageFileHandle.write(logDataCSVFileNameURL)
    staticWebPageFileHandle.write('</a>')

    staticWebPageFileHandle.write('</td></tr>')
    staticWebPageFileHandle.write('<tr><td>Seconds since the epoch</td><td>')
    staticWebPageFileHandle.write('%s</td></tr></table>' % time.time())

    staticWebPageFileHandle.write('<br><br><table>')
    staticWebPageFileHandle.write(
        '<caption>Current Configuration Values</caption>')
    staticWebPageFileHandle.write('<tr><th>Value Type</th><th>Value</th></tr>')

    linearActuatorRunTime = str(linearActuatorRunTime)
    staticWebPageFileHandle.write('<tr><td>linearActuatorRunTime</td><td>')
    staticWebPageFileHandle.write(linearActuatorRunTime)
    staticWebPageFileHandle.write(' Sec</td></tr>')

    minimumSoilMoistureSensorValue = str(minimumSoilMoistureSensorValue)
    staticWebPageFileHandle.write(
        '<tr><td>minimumSoilMoistureSensorValue</td><td>')
    staticWebPageFileHandle.write(minimumSoilMoistureSensorValue)
    staticWebPageFileHandle.write('VDC</td></tr>')

    minimumLuminositySensorValue = str(minimumLuminositySensorValue)
    staticWebPageFileHandle.write(
        '<tr><td>minimumLuminositySensorValue</td><td>')
    staticWebPageFileHandle.write(minimumLuminositySensorValue)
    staticWebPageFileHandle.write('VDC</td></tr>')

    minimumLuminositySensorValueActuatorRetract = str(
        minimumLuminositySensorValueActuatorRetract)
    staticWebPageFileHandle.write(
        '<tr><td>minimumLuminositySensorValueActuatorRetract</td><td>')
    staticWebPageFileHandle.write(minimumLuminositySensorValueActuatorRetract)
    staticWebPageFileHandle.write('VDC</td></tr>')

    minimumTemperatureActuatorRetract = str(minimumTemperatureActuatorRetract)
    staticWebPageFileHandle.write(
        '<tr><td>minimumTemperatureActuatorRetract</td><td>')
    staticWebPageFileHandle.write(minimumTemperatureActuatorRetract)
    staticWebPageFileHandle.write('F</td></tr>')

    minimumHumidityActuatorRetract = str(minimumHumidityActuatorRetract)
    staticWebPageFileHandle.write(
        '<tr><td>minimumHumidityActuatorRetract</td><td>')
    staticWebPageFileHandle.write(minimumHumidityActuatorRetract)
    staticWebPageFileHandle.write('%</td></tr>')

    minimumLuminositySensorValueActuatorExtend = str(
        minimumLuminositySensorValueActuatorExtend)
    staticWebPageFileHandle.write(
        '<tr><td>minimumLuminositySensorValueActuatorExtend</td><td>')
    staticWebPageFileHandle.write(minimumLuminositySensorValueActuatorExtend)
    staticWebPageFileHandle.write('VDC</td></tr>')

    minimumTemperatureActuatorExtend = str(minimumTemperatureActuatorExtend)
    staticWebPageFileHandle.write(
        '<tr><td>minimumTemperatureActuatorExtend</td><td>')
    staticWebPageFileHandle.write(minimumTemperatureActuatorExtend)
    staticWebPageFileHandle.write('F</td></tr>')

    minimumHumidityActuatorExtend = str(minimumHumidityActuatorExtend)
    staticWebPageFileHandle.write(
        '<tr><td>minimumHumidityActuatorExtend</td><td>')
    staticWebPageFileHandle.write(minimumHumidityActuatorExtend)
    staticWebPageFileHandle.write('%</td></tr>')

    minimumTemperatureOutputOneOn = str(minimumTemperatureOutputOneOn)
    staticWebPageFileHandle.write(
        '<tr><td>minimumTemperatureOutputOneOn</td><td>')
    staticWebPageFileHandle.write(minimumTemperatureOutputOneOn)
    staticWebPageFileHandle.write('F</td></tr>')

    minimumTemperatureOutputOneOff = str(minimumTemperatureOutputOneOff)
    staticWebPageFileHandle.write(
        '<tr><td>minimumTemperatureOutputOneOff</td><td>')
    staticWebPageFileHandle.write(minimumTemperatureOutputOneOff)
    staticWebPageFileHandle.write('F</td></tr>')

    minimumHumidityOutputOneOn = str(minimumHumidityOutputOneOn)
    staticWebPageFileHandle.write(
        '<tr><td>minimumHumidityOutputOneOn</td><td>')
    staticWebPageFileHandle.write(minimumHumidityOutputOneOn)
    staticWebPageFileHandle.write('%</td></tr>')

    minimumHumidityOutputOneOff = str(minimumHumidityOutputOneOff)
    staticWebPageFileHandle.write(
        '<tr><td>minimumHumidityOutputOneOff</td><td>')
    staticWebPageFileHandle.write(minimumHumidityOutputOneOff)
    staticWebPageFileHandle.write('%</td></tr>')

    minimumTemperatureOutputTwoOn = str(minimumTemperatureOutputTwoOn)
    staticWebPageFileHandle.write(
        '<tr><td>minimumTemperatureOutputTwoOn</td><td>')
    staticWebPageFileHandle.write(minimumTemperatureOutputTwoOn)
    staticWebPageFileHandle.write('F</td></tr>')

    minimumTemperatureOutputTwoOff = str(minimumTemperatureOutputTwoOff)
    staticWebPageFileHandle.write(
        '<tr><td>minimumTemperatureOutputTwoOff</td><td>')
    staticWebPageFileHandle.write(minimumTemperatureOutputTwoOff)
    staticWebPageFileHandle.write('F</td></tr>')

    minimumSoilMoistureSensorValueSolenoidOpen = str(
        minimumSoilMoistureSensorValueSolenoidOpen)
    staticWebPageFileHandle.write(
        '<tr><td>minimumSoilMoistureSensorValueSolenoidOpen</td><td>')
    staticWebPageFileHandle.write(minimumSoilMoistureSensorValueSolenoidOpen)
    staticWebPageFileHandle.write('VDC</td></tr>')

    minimumSoilMoistureSensorValueSolenoidClosed = str(
        minimumSoilMoistureSensorValueSolenoidClosed)
    staticWebPageFileHandle.write(
        '<tr><td>minimumSoilMoistureSensorValueSolenoidClosed</td><td>')
    staticWebPageFileHandle.write(minimumSoilMoistureSensorValueSolenoidClosed)
    staticWebPageFileHandle.write('VDC</td></tr>')
    staticWebPageFileHandle.write('</table></center><br><br>')

    staticWebPageFileHandle.write(
        '<center><a href="/wiring.png"><img src="/wiringlow.png" alt="Automation System Wiring Diagram"><a></center>')
    staticWebPageFileHandle.write('<br><br><br><br><center><a href="/em.php">Manual Operations</a></center><br><br><br><br></body></html>')
    staticWebPageFileHandle.close

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
currentLuminositySensorValue = readLuminositySensorValue()
# display the luminosity value on the LCD
currentLuminositySensorValue
writeLCDMessageContent = 'Luminosity: %s' % currentLuminositySensorValue
writeLCDMessages(writeLCDMessageContent)
# display the luminosity value via a console broadcast message
writeWallMessageContent = 'Luminosity: %s' % currentLuminositySensorValue
writeWallMessages(writeWallMessageContent)

# call our read temperature and humidity value subroutine
currentHumidity, currentTemperature = readTemperatureHumidityValues()
# display the temperature value on the LCD
writeLCDMessageContent = 'Temp: %s' % currentTemperature
writeLCDMessages(writeLCDMessageContent)
# display the temperature value via a console broadcast message
writeWallMessageContent = 'Temp: %s' % currentTemperature
writeWallMessages(writeWallMessageContent)

# display the humidity value on the LCD
writeLCDMessageContent = 'Humidity: %s' % currentHumidity
writeLCDMessages(writeLCDMessageContent)
# display the humidity value via a console broadcast message
writeWallMessageContent = 'Humidity: %s' % currentHumidity
writeWallMessages(writeWallMessageContent)

# call the read soil moisture sensor value subroutine
currentSoilMoistureSensorValue = readSoilMoistureSensorValue()
# display soil moisture sensor on the LCD
writeLCDMessageContent = 'Soil moisture: %s' % currentSoilMoistureSensorValue
writeLCDMessages(writeLCDMessageContent)
# display the soil moisture value via a console broadcast message
writeWallMessageContent = 'Soil moisture: %s' % currentSoilMoistureSensorValue
writeWallMessages(writeWallMessageContent)

# read the current solenoid valve status
solenoidStatusFileHandle = open(solenoidStatusFileName, 'r')
currentSolenoidValveStatus = solenoidStatusFileHandle.readline()
solenoidStatusFileHandle.close()
# display the solenoid value status on the LCD
writeLCDMessageContent = 'Solenoid: %s' % currentSolenoidValveStatus
writeLCDMessages(writeLCDMessageContent)
# display the solenoid value status via a console broadcast message
writeWallMessageContent = 'Solenoid: %s' % currentSolenoidValveStatus
writeWallMessages(writeWallMessageContent)

# read the current linear actuator status
actuatorStatusFileHandle = open(actuatorStatusFileName, 'r')
currentActuatorExtensionStatus = actuatorStatusFileHandle.readline()
actuatorStatusFileHandle.close()
# display the linear actuator status on the LCD
writeLCDMessageContent = 'Linear actuator: %s' % currentActuatorExtensionStatus
writeLCDMessages(writeLCDMessageContent)
# display the linear actuator status via a console broadcast message
writeWallMessageContent = 'Linear actuator: %s' % currentActuatorExtensionStatus
writeWallMessages(writeWallMessageContent)

# display the outputs status values via a console broadcast messages
outputsStatusFileHandle = open(outputsStatusFileName, 'r')
currentOutputStatusList = outputsStatusFileHandle.readlines()
outputsStatusFileHandle.close()
# remove the \n new line char from the end of the line
currentOutputStatusList[0] = currentOutputStatusList[0].strip('\n')
currentOutputStatusList[1] = currentOutputStatusList[1].strip('\n')
currentOutputStatusList[2] = currentOutputStatusList[2].strip('\n')
# display the outputs status on the LCD
writeLCDMessageContent = 'Output \#1 status: %s' % currentOutputStatusList[0]
writeLCDMessages(writeLCDMessageContent)
writeLCDMessageContent = 'Output \#2 status: %s' % currentOutputStatusList[1]
writeLCDMessages(writeLCDMessageContent)
writeLCDMessageContent = 'Output \#3 status: %s' % currentOutputStatusList[2]
writeLCDMessages(writeLCDMessageContent)
# display the outputs status via a console broadcast message
writeWallMessageContent = 'Output #1 status: %s' % currentOutputStatusList[0]
writeWallMessages(writeWallMessageContent)
writeWallMessageContent = 'Output #2 status: %s' % currentOutputStatusList[1]
writeWallMessages(writeWallMessageContent)
writeWallMessageContent = 'Output #3 status: %s' % currentOutputStatusList[2]
writeWallMessages(writeWallMessageContent)

##################################################################
##### End Reading Input Writing LCD Broadcasting Wall Message ####
##################################################################


##################################################################
#################### Begin Evaluation Process ####################
##################################################################
# begin the process of evaluating environmental conditions and
# respond accordingly

# evaulate if we close or open the window
if (currentLuminositySensorValue <= minimumLuminositySensorValueActuatorRetract and
        currentTemperature <= minimumTemperatureActuatorRetract and
        currentHumidity <= minimumHumidityActuatorRetract and
        currentSolenoidValveStatus == 'Closed'
    ):
    # retract the linear actuator and close the window
    actuatorExtensionStatus = 'Retracted'
    currentActuatorExtensionStatus = linearActuatorExtensionRetraction(
        actuatorExtensionStatus)

elif (currentLuminositySensorValue > minimumLuminositySensorValueActuatorExtend and
      currentTemperature > minimumTemperatureActuatorExtend and
      currentHumidity > minimumHumidityActuatorExtend and
      currentSolenoidValveStatus == 'Closed'
      ):
    # extend the linear actuator and open the window
    actuatorExtensionStatus = 'Extended'
    currentActuatorExtensionStatus = linearActuatorExtensionRetraction(
        actuatorExtensionStatus)

# evaulate if we need to enable output #1 turn on the fan
if (currentTemperature >= minimumTemperatureOutputOneOn or
    currentHumidity >= minimumHumidityOutputOneOn and
    currentSolenoidValveStatus == 'Closed'
    ):
    # enable output one
    outputNumber = 0
    outputStatus = 'On'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

elif (currentTemperature < minimumTemperatureOutputOneOff or
      currentHumidity < minimumHumidityOutputOneOff
      ):
    # disable output one
    outputNumber = 0
    outputStatus = 'Off'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

# evaulate if we need to enable output #2 turn on the USB heating pad
if (currentTemperature <= minimumTemperatureOutputTwoOn):
    # enable output two
    outputNumber = 1
    outputStatus = 'On'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

elif (currentTemperature > minimumTemperatureOutputTwoOff):
    # disable output two
    outputNumber = 1
    outputStatus = 'Off'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

# evaluate if the solenoid valve should be open or closed
if (currentSoilMoistureSensorValue >= minimumSoilMoistureSensorValueSolenoidOpen):
   # disable output one
    outputNumber = 0
    outputStatus = 'Off'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)
    # enable relay three opening the solenoid valve
    solenoidValveStatus = 'Open'
    solenoidValveOperation(solenoidValveStatus)

elif (currentSoilMoistureSensorValue < minimumSoilMoistureSensorValueSolenoidClosed):
    # disable relay three closing the solenoid valve
    solenoidValveStatus = 'Closed'
    solenoidValveOperation(solenoidValveStatus)

##################################################################
##################### End Evaluation Process #####################
##################################################################


##################################################################
###### Begin HTML, Database, CSV, Graph Image Update Process #####
##################################################################


# call the write static HTML output file subroutine
writeStaticHTMLFile(currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue, currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList, linearActuatorRunTime, minimumSoilMoistureSensorValue, webpageHeaderValue, minimumLuminositySensorValue, minimumLuminositySensorValueActuatorRetract, minimumTemperatureActuatorRetract,
                    minimumHumidityActuatorRetract, minimumLuminositySensorValueActuatorExtend, minimumTemperatureActuatorExtend, minimumHumidityActuatorExtend, minimumTemperatureOutputOneOn, minimumHumidityOutputOneOn, minimumTemperatureOutputOneOff, minimumHumidityOutputOneOff, minimumTemperatureOutputTwoOn, minimumTemperatureOutputTwoOff, minimumSoilMoistureSensorValueSolenoidOpen, minimumSoilMoistureSensorValueSolenoidClosed)

# call the write database table subroutine
writeDatabaseOutput(currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue,
                    currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList)

# call the write CSV output file subroutine
writeCSVOutputFile(currentLuminositySensorValue, currentTemperature, currentHumidity, currentSoilMoistureSensorValue,
                   currentSolenoidValveStatus, currentActuatorExtensionStatus, currentOutputStatusList)

# call the read database table data output graph files subroutine
readDatabaseOutputGraphs()

##################################################################
####### End HTML, Database, CSV, Graph Image Update Process ######
##################################################################
