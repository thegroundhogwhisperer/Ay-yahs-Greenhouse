# Ay-yahs-Greenhouse

# greenhousealarm.py 

A Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and sounds an audible notification using the Ubuntu speech-dispatcher when the temperature value is not between the minimum and maximum threshold.
 
Configure the greenhousealarm.py script to be executed by a crontab

$ crontab -e

Add the following line to the bottom of the current cron configuration
to execute the greenhousealarm Python script every two minutes

*/2 * * * * python3 /home/username/greenhousealarm/greenhousealarm.py

If you are using nano as your editor:

Press Ctrl-O for save

Press Enter to confirm file path and name

Press Ctrl-X to exit nano
