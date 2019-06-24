# Ay-yahs-Greenhouse

![Greenhouse Structure Image Distant](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Distant%20Small%20Image.png)

![Greenhouse Structure Image Near](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Entrance%20Small%20Image.png)

![Greenhouse Structure Interior](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Interior%20Small%20Image.png)


# Raspberry Pi Greenhouse Automation and Remote Environmental System Monitoring Project

This is a for-fun project created for the purpose of automating and remotely monitoring climate control and irrigation in a small greenhouse. System automation is achieved using an ARM based CPU (Raspberry Pi 3) in combination with a Pimoroni Automation HAT. Remote monitoring of environmental conditions is achieved through a layered communication structure. This layered communication is performed using a combination of technologies such as text-to-speech software, Python scripts, and radio frequency transmissions. The primary greenhouse automation script and support files are contained in the Greenhouse subfolder. The remote environmental system montioring Python scripts and support files are contained in the following subfolders:  Greenhousealarm, Greenhousemanualgui, Greenhousereceivedata, Greenhousestatusttsrttysstvpots, Greenhousestatusttsrttysstvrf

# Data Flow Diagram

![Data Flow Diagram Image](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Data%20Flow%20Diagram%20Small%20Image.png)

# Raspberry Pi Greenhouse Automation Project

Climate control and irrigation control is achieved by monitoring environmental sensor measurements. The environmental sensors measurements are then used to control a linear actuator, solenoid valve, small fan, and small heating pad. The information produced is displayed on a 16x2 LCD screen, broadcast via wall messages to the console, written to an html file, csv file, and SQLite database file.

# What it does

# Monitors

soil moisture

temperature

humidity

light

# Controls

linear actuator window opener

solenoid valve irrigation control

fan

heating pad

# Components

(1) Raspberry Pi - ADA3055

(1) Pimoroni Automation HAT - PIM213

(1) USB backpack kit and 16x2 RGB backlight LCD - ADA782

(1) Humidity sensor / Temperature sensor - DHT22 ADA385

(1) Soil moisture sensor - SEN0193

(1) Plastic water solenoid valve 1/2" - ADA997

(1) Linear actuator stroke 16" 12VDC

(1) Light dependent resistor - ADA997

(2) Two Channel Relay Controller - TS0619

(1) Oscillating Fan 12VDC - AC845

(1) Pump 12VDC 1.2GPM 35PSI - SFDP1-012-035-21

(1) USB pet heating pad carbon fiber

(1) 14 Watt USB LED grow light bar

# Installation

# Prerequisites

Adafruit_Python_DHT

Use pip to install from PyPI.

Python 2:

sudo pip install Adafruit_DHT

Python 3:

sudo pip3 install Adafruit_DHT

This script requires pigpiod.

Install pigpio from the Raspbian package manager:

sudo apt-get update

sudo apt-get install pigpio

pigpiod -v

Enable remote gpio access using the raspi-conf tool:

Execute raspi-config

Select menu item 5 Inferfacting Options.

Enable P8 Remote GPIO.

Choose Back

Choose Finish

Place all related file in /home/pi/Greenhouse/

Configure execute permissions on greenhouse.py, powerout.py, and camera.py.

sudo chmod +x greenhouse.py 

sudo chmod +x powerout.py 

sudo chmod +x camera.py 

The greenhouse.py script performs environmental monitoring and the conditional evaluation process. Configure cron to execute greenhouse.py, the primary automation script, every two minutes.

The powerout.py script writes file stored values, relays, and outputs to their default due to power outage. Configure cron to execute powerout.py, the power outage reset defaults script, at boot.

The camera.py script writes one high and one low resolution PNG image to /var/www/html. These images are referenced in the static HTML page generated by greenhouse.py

# Example crontab configuration

sudo crontab -e

\# reset default values, relays, and output states after a power outage

@reboot python /home/pi/Greenhouse/powerout.py

\# capture an image every five minutes

*/5 * * * * python /home/pi/Greenhouse/camera.py


crontab -e

\# execute the primary greenhouse automation script every two minutes

*/2 * * * * /usr/bin/python /home/pi/Greenhouse/greenhouse.py


# Manual operations desktop GUI screenshot

![Greenhouse Web Interface Screenshot One](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhousemanualgui/Greenhouse%20Manual%20Operations%20GUI.png)

# Web interface screenshots

![Greenhouse Web Interface Screenshot One](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Web%20Interface%20Screenshot%20One.png)

![Greenhouse Web Interface Screenshot Two](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Web%20Interface%20Screenshot%20Two.png)

# Example camera images

![Greenhouse Camera Image Animated .GIF Low Resolution](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Camera%20Image%20Animated%20Low%20Resolution.gif)


![Greenhouse Camera Image High Resolution](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Camera%20Image%20High%20Resolution.jpg)


# Wiring diagrams and enclosure images

![GreenhousePi Wiring Diagram](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Automation%20HAT%20Wiring%20Diagram%20V2%20(Smokey).png)

![Relay_Wiring Diagram](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Automation%20HAT%20Fan%20Relay%20Controller%20Wiring%20Diagram%20Small%20Image.png)

Due to the failure rate of the DHT22 sensor a power connector from a floppy disk drive is used for quick sensor replacement.

![Sensor To Berg Connector_Wiring Example](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/DHT22%20Wiring%20Example%20Berg%204%20Pin%20Peripheral%20Connector%20To%20DHT22%20Digital%20Humidity%20Temperature%20Sensor%20Greenhouse%20Small%20Image.png)

# Automation Enclosure Images

![Greenhouse Automation System Mounted Enclosure](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse%20Mounted%20Enclosure%20Small%20Image.png)

![Automation Enclosure Image](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse-Automation-Enclosure-Complete-Small-Image.png)

Two Channel Relay Enclosure image

![Two Channel Relay Enclosure Image](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Two-Channel-Relay-Enclosure-Complete-Small-Image.png)


