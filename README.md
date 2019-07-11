# Ay-yahs-Greenhouse

![Greenhouse Structure Image Distant](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Distant%20Small%20Image.png)

![Greenhouse Structure Image Near](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Entrance%20Small%20Image.png)

![Greenhouse Structure Interior](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Interior%20Small%20Image.png)


# Raspberry Pi Greenhouse Automation and Remote Environmental System Monitoring Project

This is a for-fun project created for the purpose of automating and remotely monitoring climate control and irrigation in a small greenhouse. System automation is achieved using an ARM based CPU (Raspberry Pi 3) in combination with a Pimoroni Automation HAT. Remote monitoring of environmental conditions is achieved through a layered communication structure. This layered communication is performed using a combination of technologies such as text-to-speech software, Python scripts, and radio frequency transmissions. 


# To learn more about this project please visits our wiki page here:  

https://github.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/wiki


# Example desktop interface GUI screenshot

![Greenhouse Web Interface Screenshot One](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Manual%20Operations%20GUI.png)

# Example web interface screenshot

![Greenhouse Web Interface Screenshot One](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Web%20Interface%20Screenshot%20One.png)


# Example camera images

![Greenhouse Camera Image Animated .GIF Low Resolution](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Camera%20Image%20Animated%20Low%20Resolution.gif)


![Greenhouse Camera Image High Resolution](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Images/Greenhouse%20Camera%20Image%20High%20Resolution.jpg)
























# Future modifications

Create more detailed installation instructions. Starting with a clean Debian OS.

Port the manual GUI interface as an .apk if I can ever get p4a or tivy or buildozer setup correctly.

Write a send SMS/Email script to use if the greenhouse location has internet connectivity.  The existing send SMS/Email notification script reads a RTTY log from Fldigi.  This local script could fetch and query the greenhouse.db file.

All notification scripts (e.g. greenhousealarm.py, etc.) that fetch and parse the index.csv file via wget should be recoded to fetch and query the greenhouse.db file via urllib2.  It is more efficient to query the last row of the .db file than to prase the entire index.csv file for the last line.  Using urllib2 will also eliminate the requirement of the exteral application wget.

Lots of other things...






