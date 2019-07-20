# timed operation of the solenoid valve
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

# the same power supply is used to power both output #1 and the solenoid valve 
# in Ay-yahs greenhouse. output #1 is disabled while opening the solenoid valve
# to conserve electricity in an attempt to guarantee sufficient power for the
# solenoid valves full operation.
print ("Disabling output #1 to conserve power for the solenoid valve")

# solenoid valve status file name (Open | Closed)
SOLENOID_STATUS_FILE_NAME = '/var/www/html/solenoid.txt'

# solenoid valve runtime length open value during scheduled watering
SOLENOID_VALVE_SCHEDULED_OPEN_RUNTIME_VALUE_FILE_NAME = '/var/www/html/solschruntim.txt'

# outputs status file name (On | Off)
OUTPUTS_STATUS_FILE_NAME = '/var/www/html/outputs.txt'

# read the outputs status values
outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'r')
CURRENT_OUTPUT_STATUS_LIST = outputs_status_file_handle.readlines()
outputs_status_file_handle.close()
# remove the \n new line char from the end of the line
CURRENT_OUTPUT_STATUS_LIST[0] = CURRENT_OUTPUT_STATUS_LIST[0].strip('\n')
CURRENT_OUTPUT_STATUS_LIST[1] = CURRENT_OUTPUT_STATUS_LIST[1].strip('\n')
CURRENT_OUTPUT_STATUS_LIST[2] = CURRENT_OUTPUT_STATUS_LIST[2].strip('\n')

print ("Output #1 status: ", CURRENT_OUTPUT_STATUS_LIST[0])

if (CURRENT_OUTPUT_STATUS_LIST[0] == 'On'):

	# toggle output #1 off to conserve power
	pigs_gpio_command_line = ["/usr/bin/pigs", "w 5 0"]
	p = subprocess.Popen(pigs_gpio_command_line)

# write the modified solenoid valve status to a text file
CURRENT_SOLENOID_VALVE_STATUS = 'Open'
solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
solenoid_status_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
solenoid_status_file_handle.close()

# read solenoid valve open runtime value (time in minutes)
solenoid_valve_scheduled_open_runtime_value_file_pointer = open(SOLENOID_VALVE_SCHEDULED_OPEN_RUNTIME_VALUE_FILE_NAME, 'r')
SOLENOID_VALVE_SCHEDULED_OPEN_RUNTIME_VALUE = solenoid_valve_scheduled_open_runtime_value_file_pointer.readline()
solenoid_valve_scheduled_open_runtime_value_file_pointer.close()

print ("Solenoid valve timed operation starting.")
print ("Opening the solenoid valve for the following runtime in minutes: ", SOLENOID_VALVE_SCHEDULED_OPEN_RUNTIME_VALUE)

# toggle relay #3 on to open the solenoid valve
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

# sleep before closing the solenoid valve relay
time.sleep(float(SOLENOID_VALVE_SCHEDULED_OPEN_RUNTIME_VALUE) * 60 ) 

# write the modified solenoid valve status to a text file
CURRENT_SOLENOID_VALVE_STATUS = 'Closed'
solenoid_status_file_handle = open(SOLENOID_STATUS_FILE_NAME, 'w')
solenoid_status_file_handle.write(CURRENT_SOLENOID_VALVE_STATUS)
solenoid_status_file_handle.close()

# toggle relay #3 on to close the solenoid valve
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

if (CURRENT_OUTPUT_STATUS_LIST[0] == 'On'):

	# toggle output #1 to original state of On
	pigs_gpio_command_line = ["/usr/bin/pigs", "w 5 1"]
	p = subprocess.Popen(pigs_gpio_command_line)

print ("Solenoid valve timed operation complete.")


