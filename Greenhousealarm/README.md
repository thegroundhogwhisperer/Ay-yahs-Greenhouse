# Ay-yahs-Greenhouse

# Python scripts for temperature notifictions on an Ubuntu 18.04 desktop

![Greenhouse Alarm Screenshot](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhousealarm/Greenhouse_Alarm_Screenshot.png)

# greenhousealarm.py 

A Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and determines if an audible notification should be sounded using the speech-dispatcher text-to-speech service when the temperature value is not between the minimum and maximum threshold.

# Prerequisites

Command line utility to retrieve content from a web server (wget)

Ubuntu speech-dispatcher (spd-say)

Desktop notification application (notify-send)

#
# greenhousealarm-notify-send.py 

A Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and determines if an audible notification should be sounded using the speech-dispatcher text-to-speech service and a visual indicator displayed using the desktop notification application notify-send when the temperature value is not between the minimum and maximum threshold.
 
# 
# Crontab script execution

To execute greenhousealarm.py or greenhousealarm-notify-send.py using a cron tab use a bash shell script wrapper that exports environmental variables to the Python script. Access to environmental variables allow applications to access the desktop GUI and specific users audio output devices. (e.g. notify-send, spd-say). 

# Reference

https://askubuntu.com/questions/978382/how-can-i-show-notify-send-messages-triggered-by-crontab

https://askubuntu.com/questions/719590/help-using-crontab-to-play-a-sound

#
# Example bash shell script gui-launcher wrapper contents

!#!/bin/bash -e

NAME: gui-launcher

Check whether the user is logged-in

while [ -z "$(pgrep gnome-session -n -U $UID)" ]; do sleep 3; done

!# Export the current desktop session environment variables

export $(xargs -0 -a "/proc/$(pgrep gnome-session -n -U $UID)/environ")

export XDG_RUNTIME_DIR="/run/user/1000"

export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME gnome-session)/environ)

!# Execute the input command

nohup "$@" >/dev/null 2>&1 &

exit 0

#
# Example greenhousealarm-notify-send.py execution via the bash shell wrapper script gui-launcher using a crontab executed every 20th minute

*/20 * * * * /home/username/gui-launcher "/home/username/greenhousealarm-notify-send.py"
