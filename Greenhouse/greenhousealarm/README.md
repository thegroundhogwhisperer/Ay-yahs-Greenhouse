# greenhousealarm.py is a Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format using the wget application. greenhousealarm.py evaluates the last recorded temperature value and sounds an audible notification using the Ubuntu speech-dispatcher and displays a bubble using the notify-send command when the temperature value is not between the minimum and maximum threshold.
 
# Steps for executing greenhousealarm.py at login of an Ubuntu 16 workstation.

1. Set execute permission on the greenhousealarm.py file

![Screen Shot 1](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/greenhousealarm.py%20execute%20permissions.png)

2. Select the Applications button launch Startup Applications

![Screen Shot 2](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications.png)

3. Select the Add button to add an aditional startup program

![Screen Shot 3](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications%20add%20button.png)

4. Populate a Name value (e.g. Greenhouse Alarm Python Script) and select the Browse button.

![Screen Shot 4](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications%20add%20startup%20program%20browse%20button.png)

5. Navigate to and select the greenhousealarm.py file

![Screen Shot 5](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications%20add%20select%20command.png)

6. Select the Open button

![Screen Shot 6](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications%20add%20select%20command%20open%20button.png)

7. Select the Add button

![Screen Shot 7](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications%20add%20startup%20program%20add%20button.png)

8. Select the Close button

![Screen Shot 8](https://raw.githubusercontent.com/thegroundhogwhisperer/Ay-yahs-Greenhouse/master/Greenhouse/greenhousealarm/screenshots/ubuntu%20startup%20applications%20close%20button.png)

9. Logout and back in to start the greenhousealarm.py script

