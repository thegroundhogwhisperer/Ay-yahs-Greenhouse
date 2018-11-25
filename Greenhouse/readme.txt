Install Adafruit_Python_DHT.
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

Configure execute permissions on greenhouse.py and powerout.py.
sudo chmod +x greenhouse.py 
sudo chmod +x powerout.py 

The script powerout.py writes file stored values, relays, and
outputs to their default due to power outage.
Configure cron to execute powerout.py at boot.

Configure cron to execute greenhouse.py, the primary automation
script every two minutes.

The script camera.py captures a still camea image as greenhouse.jpg.
Configure cron to execute camera.py every five minutes.

Example crontab configuration.
sudo crontab -e
# reset default values, relays, and output states after a power outage
@reboot python /home/pi/Greenhouse/powerout.py

# execute the pistreaming script at boot
# if the live stream server.py script is running
# camera.py will be unable to access the camera
#@reboot /usr/bin/python3 /home/pi/pistreaming/server.py

# execute the greetings boot messages on the 16x2 LCD
@reboot python /home/pi/Greenhouse/lcd.py

# capture an image every five minutes
*/5 * * * * python /home/pi/Greenhouse/camera.py

# execute the primary greenhouse automation script
#*/2 * * * * python /home/pi/Greenhouse/greenhouse.py

crontab -e
# execute the primary greenhouse automation script every two minutes
*/2 * * * * /usr/bin/python /home/pi/Greenhouse/greenhouse.py


Modifications are need to resolve issues pistreaming/server.py has
with relative paths.  
Reference:  https://www.timpoulsen.com/2018/pi-birdcam.html



