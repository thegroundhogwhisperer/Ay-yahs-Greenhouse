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

import subprocess
import statistics
import serial
import math
import Adafruit_DHT
import time
import automationhat
time.sleep(0.1)  # short pause after ads1015 class creation recommended

##################################################################
###################### Customizable Values #######################
##################################################################

# linear actuator status filename
actuatorStatusFileName = '/home/pi/Greenhouse/actuator.txt'
# solenoid valve status filename
solenoidStatusFileName = '/home/pi/Greenhouse/solenoid.txt'
# outputs status filename
outputsStatusFileName = '/home/pi/Greenhouse/outputs.txt'

# static webpage file name
staticWebPageFileName = "/var/www/html/index.html"

# CSV file name containing log data
logDataCSVFileName = "/var/www/html/index.csv"

# this actuators stroke is 406.4 mm at 10 mm per second
# wait 40.6 seconds to open the window
linearActuatorRunTime = 40.6

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
minimumTemperatureOutputOneOn = 80
minimumHumidityOutputOneOn = 70

# minimum temp or humidity values output #1 turn off the fan
minimumTemperatureOutputOneOff = 79
minimumHumidityOutputOneOff = 68

# minimum temp value output #2 turn on the USB heating pad
minimumTemperatureOutputTwoOn = 35

# minimum temp value output #2 turn off the USB heating pad
minimumTemperatureOutputTwoOff = 40

# minimum soil moisture value relay #3 open solenoid valve
minimumSoilMoistureSensorValueSolenoidOpen = 1.9

# minimum soil moisture value relay #3 close solenoid valve
minimumSoilMoistureSensorValueSolenoidClosed = 1.6

##################################################################
#################### End Customizable Values #####################
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
    p = subprocess.Popen(wallMessageCommandLine)


##################################################################
#################### Begin Evaluation Process ####################
##################################################################
# begin the process of evaluating environmental conditions and respond accordingly
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


# evaulate if we close or open the window
if (currentLuminositySensorValue <= minimumLuminositySensorValueActuatorRetract and
    # if ( currentLuminositySensorValue <= 1 and

    currentTemperature <= minimumTemperatureActuatorRetract and
    currentHumidity <= minimumHumidityActuatorRetract
    ):
    # retract the linear actuator and close the window
    actuatorExtensionStatus = 'Retracted'
    currentActuatorExtensionStatus = linearActuatorExtensionRetraction(
        actuatorExtensionStatus)

elif (currentLuminositySensorValue >= minimumLuminositySensorValueActuatorExtend and
      currentTemperature >= minimumTemperatureActuatorExtend and
      currentHumidity >= minimumHumidityActuatorExtend
      ):
    # extend the linear actuator and open the window
    actuatorExtensionStatus = 'Extended'
    currentActuatorExtensionStatus = linearActuatorExtensionRetraction(
        actuatorExtensionStatus)

   # evaulate if we need to enable output #1 turn on the fan
if (currentTemperature >= minimumTemperatureOutputOneOn or
    currentHumidity >= minimumHumidityOutputOneOn
    ):
    outputNumber = 0
    outputStatus = 'On'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

elif (currentTemperature <= minimumTemperatureOutputOneOff or
      currentHumidity <= minimumHumidityOutputOneOff
      ):
    outputNumber = 0
    outputStatus = 'Off'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

   # evaulate if we need to enable output #2 turn on the USB heating pad
if (currentTemperature <= minimumTemperatureOutputTwoOn):
    outputNumber = 1
    outputStatus = 'On'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

elif (currentTemperature >= minimumTemperatureOutputTwoOff):
    outputNumber = 1
    outputStatus = 'Off'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

# call the read soil moisture sensor value subroutine
currentSoilMoistureSensorValue = readSoilMoistureSensorValue()
# display soil moisture sensor on the LCD
writeLCDMessageContent = 'Soil moisture: %s' % currentSoilMoistureSensorValue
writeLCDMessages(writeLCDMessageContent)
# display the soil moisture value via a console broadcast message
writeWallMessageContent = 'Soil moisture: %s' % currentSoilMoistureSensorValue
writeWallMessages(writeWallMessageContent)

# evaluate if output 1 should be on or off
if (currentSoilMoistureSensorValue >= minimumSoilMoistureSensorValueSolenoidOpen):

    solenoidValveStatus = 'Open'
    solenoidValveOperation(solenoidValveStatus)

elif (currentSoilMoistureSensorValue <= minimumSoilMoistureSensorValueSolenoidClosed):
    solenoidValveStatus = 'Closed'
    solenoidValveOperation(solenoidValveStatus)

##################################################################
##################### End Evaluation Process #####################
##################################################################

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

<meta http-equiv="refresh" content="120">

<title>Greenhouse Automation System Status Information</title></head>

<body bgcolor="#CCFFFF">
""")

staticWebPageFileHandle.write('<h3 align="center">')
staticWebPageFileHandle.write(webpageHeaderValue)
staticWebPageFileHandle.write('<br>Status Information</h3>')

staticWebPageFileHandle.write(
    '<a href="/greenhousehigh.jpg"><center><img src="/greenhouselow.jpg" alt="Greenhouse Camera Image"><br>Click for high resolution</center></a>')
staticWebPageFileHandle.write('<center><table>')
staticWebPageFileHandle.write('<caption>Current Environmental Data</caption>')
staticWebPageFileHandle.write('<tr><th>Reading Type</th><th>Value</th></tr>')

currentLuminositySensorValue = str(currentLuminositySensorValue)
staticWebPageFileHandle.write('<tr><td>')
staticWebPageFileHandle.write('Luminosity</td><td>')
staticWebPageFileHandle.write(currentLuminositySensorValue)
staticWebPageFileHandle.write('VDC</td></tr>')

currentTemperature = str(currentTemperature)
staticWebPageFileHandle.write('<tr><td>Temperature</td><td>')
staticWebPageFileHandle.write(currentTemperature)
staticWebPageFileHandle.write('F</td></tr>')

currentHumidity = str(currentHumidity)
staticWebPageFileHandle.write('<tr><td>Humidity</td><td>')
staticWebPageFileHandle.write(currentHumidity)
staticWebPageFileHandle.write('%</td></tr>')

currentSoilMoistureSensorValue = str(currentSoilMoistureSensorValue)
staticWebPageFileHandle.write('<tr><td>Soil moisture</td><td>')
staticWebPageFileHandle.write(currentSoilMoistureSensorValue)
staticWebPageFileHandle.write('VDC</td></tr>')

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
staticWebPageFileHandle.write('<a href="/index.csv">index.csv</a>')

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
staticWebPageFileHandle.write('<tr><td>minimumLuminositySensorValue</td><td>')
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
staticWebPageFileHandle.write('<tr><td>minimumHumidityOutputOneOn</td><td>')
staticWebPageFileHandle.write(minimumHumidityOutputOneOn)
staticWebPageFileHandle.write('%</td></tr>')

minimumHumidityOutputOneOff = str(minimumHumidityOutputOneOff)
staticWebPageFileHandle.write('<tr><td>minimumHumidityOutputOneOff</td><td>')
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

staticWebPageFileHandle.write('</body></html>')

staticWebPageFileHandle.close


# begin file append of CSV file to the web server root
# "Luminosity","Temperature","Humidity","Moisture",
# "Solenoid","Actuator","Output1","Output2","Output3","Epoch"

csvFileHandle = open(logDataCSVFileName, "a")

csvFileHandle.write('"')
csvFileHandle.write(currentLuminositySensorValue)
csvFileHandle.write('",\"')

csvFileHandle.write('')
csvFileHandle.write(currentTemperature)
csvFileHandle.write('","')

csvFileHandle.write('')
csvFileHandle.write(currentHumidity)
csvFileHandle.write('","')

csvFileHandle.write('')
csvFileHandle.write(currentSoilMoistureSensorValue)
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

staticWebPageFileHandle.close
