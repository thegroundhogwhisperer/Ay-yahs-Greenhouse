# Ay-yahs-Greenhouse

# Python script for VOX activated radio frequency broadcast transmissions containing audible notifications of greenhouse environmental conditions on an Ubuntu 18 desktop 

# Warning: Laws governing the operation of a radio frequency transceiver or transmitter are clearly established and strictly enforced by federal regulations.

# Prerequisites

Command line utility to retrieve content from a web server (wget)

Ubuntu speech-dispatcher (spd-say)

Desktop notification application (notify-send)

# Variants

# /without_notify-send/greenhousestatuscronttsrf.py	

Python script configured for execution from a crontab that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousestatusstartupttsrf.py produces text-to-speech using the Ubuntu speech-dispatcher containing the current greenhouse environmental status. The text-to-speech audio output can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse environmental conditions.

# /without_notify-send/greenhousestatusstartupttsrf.py
 
Python script configured for execution from the Ubuntu Startup Applications GUI that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousestatusstartupttsrf.py produces text-to-speech using the Ubuntu speech-dispatcher containing the current greenhouse environmental status. The text-to-speech audio output can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse environmental conditions. 

# /with_notify-send/greenhousestatuscronttsrf.py

Python script configured for execution from a crontab that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousestatusstartupttsrf.py produces text-to-speech using the Ubuntu speech-dispatcher containing the current greenhouse environmental status. The text-to-speech audio output can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse environmental conditions. This variant also displays visual notifications using the notify-send desktop notification program.

# /with_notify-send/greenhousestatusstartupttsrf.py

Python script configured for execution from the Ubuntu Startup Applications GUI that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousestatusstartupttsrf.py produces text-to-speech using the Ubuntu speech-dispatcher containing the current greenhouse environmental status. The text-to-speech audio output can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse environmental conditions. This variant also displays visual notifications using the notify-send desktop notification program.


# Prerequisites

Command line utility to retrieve content from a web server (wget)

Ubuntu speech-dispatcher (spd-say)

Desktop notification application (notify-send)

General-purpose software audio FSK modem (minimodem)

# /with_notify-send/greenhousestatuscronttsrfmodem.py

Python script configured for execution from a crontab that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousestatusstartupttsrf.py produces text-to-speech using the Ubuntu speech-dispatcher containing the current greenhouse environmental status. The text-to-speech audio output can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse environmental conditions. This variant also displays visual notifications using the notify-send desktop notification program. This variant also uses minimodem to convert the greenhouse environmental status into a RTTY (radioteletype) audio file that is broadcast via a VOX transciever.

# /without_notify-send/greenhousestatuscronttsrfmodem.py	

Python script configured for execution from a crontab that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousestatusstartupttsrf.py produces text-to-speech using the Ubuntu speech-dispatcher containing the current greenhouse environmental status. The text-to-speech audio output can be connected to a radio in VOX (voice-operated exchange) mode allowing for radio frequency transmission of the current greenhouse environmental conditions. This variant also uses minimodem to convert the greenhouse environmental status into a RTTY (radioteletype) audio file that is broadcast via a VOX transciever.


