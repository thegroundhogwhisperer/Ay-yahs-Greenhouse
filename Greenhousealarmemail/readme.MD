# greenhouseemailalarm.py 

# Ay-yah's Greenhouse server email/SMS alarm notification script

This script runs on the GreenhousePi and sends email/SMS notifications when temperature values are too high or low or soil moisture values are too high. 

# Example execution using cron and a crontab

$ sudo crontab -e

*/30 * * * * python /home/pi/Greenhouse/greenhousealarmemail.py

