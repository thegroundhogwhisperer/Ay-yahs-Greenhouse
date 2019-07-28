# timed operation of the linear actuator
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

# Linear actuator status file name (Retracted | Extended)
ACTUATOR_STATUS_FILE_NAME = '/var/www/html/actuator.txt'

# Linear actuator runtime value file name (seconds)
LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME = '/var/www/html/actuatorruntime.txt'

try:
	# Read the current linear actuator runtime value from a file
	actuator_runtime_value_file_handle = open(LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME, 'r')
	LINEAR_ACTUATOR_RUN_TIME_VALUE = actuator_runtime_value_file_handle.readline()
	actuator_runtime_value_file_handle.close()
	
except OSError:

	print ("An error occurred writing file name: ", LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME)
	quit()


# Linear actuator extension runtime length value during scheduled linear actuator regulation
LINEAR_ACTUATOR_SCHEDULED_EXTEND_RUNTIME_VALUE_FILE_NAME = '/var/www/html/linschruntim.txt'

try:
	# read linear actuator extension runtime value (time in minutes)
	linear_actuator_scheduled_extension_runtime_value_file_pointer = open(LINEAR_ACTUATOR_SCHEDULED_EXTEND_RUNTIME_VALUE_FILE_NAME, 'r')
	LINEAR_ACTUATOR_SCHEDULED_EXTEND_RUNTIME_VALUE = linear_actuator_scheduled_extension_runtime_value_file_pointer.readline().rstrip('\n')
	linear_actuator_scheduled_extension_runtime_value_file_pointer.close()
	
except OSError:

	print ("An error occurred writing file name: ", LINEAR_ACTUATOR_SCHEDULED_EXTEND_RUNTIME_VALUE_FILE_NAME)
	quit()


print ("Linear actuator scheduled extension operation starting.\n")
print ("Linear actuator runtime in seconds: ", LINEAR_ACTUATOR_RUN_TIME_VALUE)
print ("Extending the linear acutator for the following time in minutes: ", LINEAR_ACTUATOR_SCHEDULED_EXTEND_RUNTIME_VALUE)

# toggle relay #1 on to extend the linear actuator
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 13 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

time.sleep(float(LINEAR_ACTUATOR_RUN_TIME_VALUE))

# toggle relay #1 off
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 13 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

CURRENT_ACTUATOR_EXTENSION_STATUS = "Extended"


try: 
	# Write the modified status to a text file
	actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'w')
	actuator_status_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
	actuator_status_file_handle.close()
	
except OSError:

	print ("An error occurred writing file name: ", ACTUATOR_STATUS_FILE_NAME)
	quit()



print ("Linear actuator scheduled extension operation complete.")


# sleep before retracting the linear actuator
time.sleep(float(LINEAR_ACTUATOR_SCHEDULED_EXTEND_RUNTIME_VALUE) * 60 ) 

print ("Linear actuator scheduled retraction operation starting.")

# toggle relay #2 on to retract the linear actuator
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 19 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

time.sleep(float(LINEAR_ACTUATOR_RUN_TIME_VALUE))

# toggle relay #2 off
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 19 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

CURRENT_ACTUATOR_EXTENSION_STATUS = "Retracted"

try: 

	# Write the modified status to a text file
	actuator_status_file_handle = open(ACTUATOR_STATUS_FILE_NAME, 'w')
	actuator_status_file_handle.write(CURRENT_ACTUATOR_EXTENSION_STATUS)
	actuator_status_file_handle.close()


except OSError:

	print ("An error occurred writing file name: ", ACTUATOR_STATUS_FILE_NAME)
	quit()


print ("Linear actuator scheduled retraction operation complete.")


