#!/usr/bin/env python
#encoding: utf-8

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

import subprocess
import serial
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

# this actuators stroke is 406.4 mm at 10 mm per second
# wait 40.6 seconds to open the window
linearActuatorRunTime = 40.6

# set the minimum value at 0.05VDC
minimumSoilMoistureSensorValue = 0.05

# set the minimum luminosity sensors value at 0.05VDC
minimumLuminositySensorValue = 0.05

# define the 16x2 RGB LCD device name connect via USB serial backpack kit
serialLCDDeviceName = '/dev/ttyACM0'

# define the length of time in seconds to display each message on the LCD
# screen
displayLCDMessageLength = .9

# minimum light and temp and humidity values relay #2 close the window
minimumLuminositySensorValueActuatorRetract = 0.25
minimumTemperatureActuatorRetract = 80
minimumHumidityActuatorRetract = 90

# minimum light and temp and humidity values relay #1 open the window
minimumLuminositySensorValueActuatorExtend = 0.26
minimumTemperatureActuatorExtend = 50
minimumHumidityActuatorExtend = 20

# minimum temp or humidity values output #1 turn on the fan
minimumTemperatureOutputOneOn = 80
minimumHumidityOutputOneOn = 70

# minimum temp or humidity values output #1 turn off the fan
minimumTemperatureOutputOneOff = 79
minimumHumidityOutputOneOff = 50

# minimum temp value output #2 turn on the USB heating pad
minimumTemperatureOutputTwoOn = 49

# minimum temp value output #2 turn off the USB heating pad
minimumTemperatureOutputTwoOff = 50

# minimum soil moisture value relay #3 open solenoid valve
minimumSoilMoistureSensorValueSolenoidOpen = 2.0

# minimum soil moisture value relay #3 close solenoid valve
minimumSoilMoistureSensorValueSolenoidClosed = 1.1

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
                    'DHT sensor error humidity value greater than 100 = %.2f Attempting reread' %
                    currentHumidity)

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
        print('Output %d already in the desired state' % outputNumber)
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
        print(
            'Linear actuator already in state: %s' %
            currentActuatorExtensionStatus)
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
        print(
            'Solenoid valve already in state: %s' %
            currentSolenoidValveStatus)
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
    for i in range(0, 10):
        try:

            # read the moisture value from analog to digital converter #1
            currentSoilMoistureSensorValue = automationhat.analog[0].read()
            time.sleep(0.5)
            if (currentSoilMoistureSensorValue <
                    minimumSoilMoistureSensorValue):
                print(
                    'ADC error read soil moisture value less than 0.05VDC = %.2f Attempting reread' %
                    currentSoilMoistureSensorValue)

            if (currentSoilMoistureSensorValue >
                    minimumSoilMoistureSensorValue):
                return(currentSoilMoistureSensorValue)
                break

        except RuntimeError as e:
            # print an error if the sensor read fails
            print("ADC sensor read failed: ", e.args)


# analog to digital converter #2 read light dependent resistor value subroutine
def readLuminositySensorValue():

    # the ADC may produce an erroneous luminisoty reading less than 0.05VDC
    # a for loop retrys the read process until a value > 0.05VDC is returned
    for i in range(0, 10):
        try:

            # read the light value from analog to digital converter #2
            currentLuminositySensorValue = automationhat.analog[1].read()
            currentLuminositySensorValue = automationhat.analog[1].read()
            currentLuminositySensorValue = automationhat.analog[1].read()
            time.sleep(0.5)

            if (currentLuminositySensorValue < minimumLuminositySensorValue):
                print(
                    'ADC error read LDR value less than 0.05VDC = %0.2f Attempting reread' %
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
    print(wallMessageText)
    wallMessageCommandLine = ['wall', '-n', wallMessageText]
    p = subprocess.Popen(wallMessageCommandLine)



# begin the process of evaluating environmental conditions and respond accordingly
# call the read luminosity sensor value subroutine
currentLuminositySensorValue = readLuminositySensorValue()
print("The light dependent resistor value is:")
print(currentLuminositySensorValue)
# display the luminosity value on the LCD
# convert to a floating point
currentLuminositySensorValueFloat = float(currentLuminositySensorValue)
writeLCDMessageContent = 'Luminosity: %.2f' % currentLuminositySensorValueFloat
writeLCDMessages(writeLCDMessageContent)
# display the luminosity value via a console broadcast message
writeWallMessageContent = 'Luminosity: %.2f' % currentLuminositySensorValueFloat
writeWallMessages(writeWallMessageContent)


# call our read temperature and humidity value subroutine
currentHumidity, currentTemperature = readTemperatureHumidityValues()
print("Our temperature value is:")
print(currentTemperature)
# display the temperature value on the LCD
writeLCDMessageContent = 'Temp: %.2f' % currentTemperature
writeLCDMessages(writeLCDMessageContent)
# display the temperature value via a console broadcast message
writeWallMessageContent = 'Temp: %.2f' % currentTemperature
writeWallMessages(writeWallMessageContent)

print("Our humidity value is:")
print(currentHumidity)
# display the humidity value on the LCD
writeLCDMessageContent = 'Humidity: %.2f' % currentHumidity
writeLCDMessages(writeLCDMessageContent)
# display the humidity value via a console broadcast message
writeWallMessageContent = 'Humidity: %.2f' % currentHumidity
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
    outputNumber = 0
    outputStatus = 'On'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

elif (currentTemperature >= minimumTemperatureOutputTwoOff):
    outputNumber = 1
    outputStatus = 'Off'
    currentOutputStatus = controlOutputs(outputNumber, outputStatus)

# call the read soil moisture sensor value subroutine
currentSoilMoistureSensorValue = readSoilMoistureSensorValue()
# display soil moisture sensor on the LCD
writeLCDMessageContent = 'Soil moisture: %.2f' % currentSoilMoistureSensorValue
writeLCDMessages(writeLCDMessageContent)
print("The soil moisture value is:")
currentSoilMoistureSensorValue = int(float(currentSoilMoistureSensorValue))
print(currentSoilMoistureSensorValue)
# display the soil moisture value via a console broadcast message
writeWallMessageContent = 'Soil moisture: %.2f' % currentSoilMoistureSensorValue
writeWallMessages(writeWallMessageContent)

# evaluate if output 1 should be on or off
if (currentSoilMoistureSensorValue >= minimumSoilMoistureSensorValueSolenoidOpen):

    solenoidValveStatus = 'Open'
    solenoidValveOperation(solenoidValveStatus)

elif (currentSoilMoistureSensorValue <= minimumSoilMoistureSensorValueSolenoidClosed):
    solenoidValveStatus = 'Closed'
    solenoidValveOperation(solenoidValveStatus)


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

print("The solenoid value status is:")
print(currentSolenoidValveStatus)

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
print("The linear actuator status is:")
print(currentActuatorExtensionStatus)


# display the outputs status values via a console broadcast messages
outputsStatusFileHandle = open(outputsStatusFileName, 'r')
currentOutputStatusList = outputsStatusFileHandle.readlines()
outputsStatusFileHandle.close()
# remove the \n new line char from the end of the line
currentOutputStatusList[0] = currentOutputStatusList[0].strip('\n')
currentOutputStatusList[1] = currentOutputStatusList[1].strip('\n')
currentOutputStatusList[2] = currentOutputStatusList[2].strip('\n')
# display the outputs status on the LCD
writeLCDMessageContent = r'Output \#1 status: %s' % currentOutputStatusList[0]
writeLCDMessages(writeLCDMessageContent)
writeLCDMessageContent = r'Output \#2 status: %s' % currentOutputStatusList[1]
writeLCDMessages(writeLCDMessageContent)
writeLCDMessageContent = r'Output \#3 status: %s' % currentOutputStatusList[2]
writeLCDMessages(writeLCDMessageContent)
# display the outputs status via a console broadcast message
writeWallMessageContent = 'Output #1 status: %s' % currentOutputStatusList[0]
writeWallMessages(writeWallMessageContent)
writeWallMessageContent = 'Output #2 status: %s' % currentOutputStatusList[1]
writeWallMessages(writeWallMessageContent)
writeWallMessageContent = 'Output #3 status: %s' % currentOutputStatusList[2]
writeWallMessages(writeWallMessageContent)

