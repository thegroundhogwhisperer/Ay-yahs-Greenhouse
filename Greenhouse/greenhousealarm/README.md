# greenhousealarm.py 

A Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and sounds an audible notification using the Ubuntu speech-dispatcher when the temperature value is not between the minimum and maximum threshold.
 
Configure the greenhousealarm.py script to be executed by a crontab

$ crontab -e
## Edit this file to introduce tasks to be run by cron.
## 
## Each task to run has to be defined through a single line
## indicating with different fields when the task will be run
## and what command to run for the task
## 
## To define the time you can provide concrete values for
## minute (m), hour (h), day of month (dom), month (mon),
## and day of week (dow) or use '*' in these fields (for 'any').# 
## Notice that tasks will be started based on the cron's system
## daemon's notion of time and timezones.
## 
## Output of the crontab jobs (including errors) is sent through
## email to the user the crontab file belongs to (unless redirected).
## 
## For example, you can run a backup of all your user accounts
## at 5 a.m every week with:
## 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
## 
## For more information see the manual pages of crontab(5) and cron(8)
## 
## m h  dom mon dow   command

Add the following line to the bottom of the current cron configuration

# */1 * * * * python3 /home/username/greenhousealarm/greenhousealarm.py

If you are using nano as your editor:

Press Ctrl-O for save
Press Enter to confirm file path and name
Press Ctrl-X to exit nano


