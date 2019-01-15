# Ay-yahs-Greenhouse

# Python script for temperature notifictions on an Ubuntu 18.04 desktop.

# greenhousealarm.py 

A Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and determines if an audible notification should be sounded using the speech-dispatcher text-to-speech service when the temperature value is not between the minimum and maximum threshold.
 
Configure the greenhousealarm.py script to be executed by a crontab

$ crontab -e

Add the following line to the bottom of the current cron configuration
to execute the greenhousealarm Python script every two minutes

*/2 * * * * python3 /home/username/greenhousealarm/greenhousealarm.py

# greenhousealarm-notify-send.py 

A Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and determines if an audible notification should be sounded using the speech-dispatcher text-to-speech service and a visual indicator displayed using the desktop notification application notify-send when the temperature value is not between the minimum and maximum threshold.
 
Configure the greenhousealarm.py script to be executed by a crontab

$ crontab -e

Add the following line to the bottom of the current cron configuration
to execute the greenhousealarm Python script every two minutes. 

The eval command specifies which display notify-send will use to display alerts.

*/2 * * * * eval "export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME gnome-session)/environ)"; python3 /home/username/greenhousealarm/greenhousealarm-notify-send.py

If you are using nano as your editor:

Press Ctrl-O for save

Press Enter to confirm file path and name

Press Ctrl-X to exit nano

