# Ay-yahs-Greenhouse


# Python script for a graphical greenhouse manual operations interface


# greenhousegtkcontrol.py

![Greenhouse Manual Control GTK GUI](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhousealarm/Greenhouse_Alarm_Screenshot.png)



# Requirements: 

python-gi

Python


# 
# Produces:


A graphical user inferface that allows a user perform manual greenhouse operations. (e.g. Open the greenhouse window, turn off the fan, turn on the light, etc.)

# Application icon setup on Ubuntu

Copy the greenhousegtkcontrol.py and headerimage.jpg files to your desired installation destination.  (e.g. /home/username/)
Configure the greenhousegtkcontrol.py file permissions to allow execution.  (e.g. chmod +X /home/username/greenhousegtkcontrol.py)

Configure the greenhouse.desktop file using a text editor (e.g. nano, gedit, etc.) for the appropirate file path configuration.

Copy the greenhouse.desktop to your operating systems /applications folder. (e.g. /home/username/.local/share/applications/)
Configure the greenhouse.desktop file permissions to allow execution.  (e.g. sudo chmod +X /home/username/.local/share/applications/greenhouse.desktop)

# Example contents of greenhouse.desktop

[Desktop Entry]# Ay-yahs-Greenhouse


# Python script for a graphical greenhouse manual operations interface


# greenhousegtkcontrol.py


# Requirements: 

python-gi

Python

 
# Produces:

A graphical user inferface that allows a user perform manual greenhouse operations. (e.g. Open the greenhouse window, turn off the fan, turn on the light, etc.)


# Application icon setup on Ubuntu

Copy the greenhousegtkcontrol.py and headerimage.jpg files to your desired installation destination.  (e.g. /home/username/)
Configure the greenhousegtkcontrol.py file permissions to allow execution.  (e.g. chmod +X /home/username/greenhousegtkcontrol.py)

Configure the greenhouse.desktop file using a text editor (e.g. nano, gedit, etc.) for the appropirate file path configuration.

Name=Ay-yah's Greenhouse Manual Control Interface
Exec=/home/username/greenhousegtkcontrol.py
Icon=/home/username/headerimage.jpg
Terminal=true
Type=Application
