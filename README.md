# Ay-yahs-Greenhouse

![Greenhouse Structure Image Distant](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Distant%20Small%20Image.png)

![Greenhouse Structure Image Near](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Entrance%20Small%20Image.png)

![Greenhouse Structure Interior](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Interior%20Small%20Image.png)


# Raspberry Pi Greenhouse Automation and Remote Environmental System Monitoring Project

This is a for-fun project created for the purpose of automating and remotely monitoring climate control and irrigation in a small greenhouse. System automation is achieved using an ARM based CPU (Raspberry Pi 3) in combination with a Pimoroni Automation HAT. Remote monitoring of environmental conditions is achieved through a layered communication structure. This layered communication is performed using a combination of technologies such as text-to-speech software, Python scripts, and radio frequency transmissions. The primary greenhouse automation script and support files are contained in the Greenhouse subfolder. The remote environmental system montioring Python scripts and support files are contained in the following subfolders:  Greenhousealarm, Greenhousemanualgui, Greenhousereceivedata, Greenhousestatusttsrttysstvpots, Greenhousestatusttsrttysstvrf

# To learn more about this project please visits our wiki page here:  

https://github.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/wiki


# Example manual operations desktop GUI screenshot

![Greenhouse Web Interface Screenshot One](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Manual%20Operations%20GUI.png)

# Example web interface screenshots

![Greenhouse Web Interface Screenshot One](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Web%20Interface%20Screenshot%20One.png)


# Example camera images

![Greenhouse Camera Image Animated .GIF Low Resolution](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Camera%20Image%20Animated%20Low%20Resolution.gif)


![Greenhouse Camera Image High Resolution](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Camera%20Image%20High%20Resolution.jpg)












# Future modifications

Add a configuration option setting the mode (variable 0 = heating pad or 1 = grow light) to allow switching between the evaluation of environmental conditions for the purpose of regulating a heating pad or regulating a grow light on Output 2. Done!

Write the system configuration values to files on the disk (e.g. The minimum soil moisture value  /home/greenhouse/minimumsoilmoisture.txt) with the intent of the file/value being remotely modified via the web interface. Done!

The system configuration values are currently constants in the main greenhouse.py application code. Not any longer; they are values stored in text files on the disk in the /var/www/html/ folder. Done!

A .php or .py script could receive form submission data from the greenhousegtkcontrol.py manual GUI interface script via urllib2 providing a method of remotely updating system configuration values stored on the GreenhousePi's disk.

A .php script now reads form submission data allowing for remote configuration of system values. Done!

This same index.php script can be used to parse POST submissions from a Python based GTK GUI application submitting from data using urllib2.

Create more detailed installation instructions. Starting with a clean Debian OS.  I need to start a wiki for this and produce some viable documentation.

Fix the graphs.... Done!

Port the manual GUI interface as an .apk if I can ever get p4a or tivy or buildozer setup correctly.

Move all the images in this repositories root folder to their own folder/directory and update the links in this document. Done!

Write a log file for manually performed procedures (e.g. Activation of the solenoid valve.) I dunno... maybe not...

Write a lovely Flask interface.  Wrote a lovely .php interface that will suffice for now.  Done!

Write remote configuration features for setting the environmental condition values (e.g. Luminosity value returned selecting when to turn off output 2).  Done!

Write a send SMS/Email script to use if the greenhouse location has internet connectivity.  The existing send SMS/Email notification script reads a RTTY log from Fldigi.  This local script could fetch and query the greenhouse.db file.

All notification scripts (e.g. greenhousealarm.py, etc.) that fetch and parse the index.csv file via wget should be recoded to fetch and query the greenhouse.db file via urllib2.  It is more efficient to query the last row of the .db file than to prase the entire index.csv file for the last line.  Using urllib2 will also eliminate the requirement of the exteral application wget.

Need to create a flow diagram of greenhouse.py

Lots of other things...






