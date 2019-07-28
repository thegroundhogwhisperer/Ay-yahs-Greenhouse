# timed operation of output one
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

# Outputs status file name (On | Off)
OUTPUTS_STATUS_FILE_NAME = '/var/www/html/outputs.txt'

try:
	outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'r')
	CURRENT_OUTPUT_STATUS_LIST = outputs_status_file_handle.readlines()
	outputs_status_file_handle.close()
	print ("Read CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2] from file", CURRENT_OUTPUT_STATUS_LIST[0], CURRENT_OUTPUT_STATUS_LIST[1], CURRENT_OUTPUT_STATUS_LIST[2])
	# Remove the \n new line char from the end of the line
	CURRENT_OUTPUT_STATUS_LIST[0] = CURRENT_OUTPUT_STATUS_LIST[0].rstrip('\n')
	#CURRENT_OUTPUT_STATUS_LIST[1] = CURRENT_OUTPUT_STATUS_LIST[1].rstrip('\n')
	#CURRENT_OUTPUT_STATUS_LIST[2] = CURRENT_OUTPUT_STATUS_LIST[2].rstrip('\n')
	
except OSError:

	print ("An error occurred reading file name: ", OUTPUTS_STATUS_FILE_NAME)
	quit()

# Linear actuator extension runtime length value during scheduled linear actuator regulation
OUTPUT_ONE_SCHEDULED_ENABLE_RUNTIME_VALUE_FILE_NAME = '/var/www/html/outoneschruntim.txt'

try:
	# read linear actuator extension runtime value (time in minutes)
	output_one_scheduled_enable_runtime_value_file_pointer = open(OUTPUT_ONE_SCHEDULED_ENABLE_RUNTIME_VALUE_FILE_NAME, 'r')
	OUTPUT_ONE_SCHEDULED_ENABLE_RUNTIME_VALUE = output_one_scheduled_enable_runtime_value_file_pointer.readline().rstrip('\n')
	output_one_scheduled_enable_runtime_value_file_pointer.close()
	
except OSError:

	print ("An error occurred reading file name: ", OUTPUT_ONE_SCHEDULED_ENABLE_RUNTIME_VALUE_FILE_NAME)
	quit()

print ("Output one scheduled on operation starting.")
print ("Enabling output one for the following time in minutes: ", OUTPUT_ONE_SCHEDULED_ENABLE_RUNTIME_VALUE)

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

CURRENT_OUTPUT_STATUS_LIST[0] = "On\n"

try: 
	# Write the modified status to a text file
	outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'w')
	outputs_status_file_handle.writelines(CURRENT_OUTPUT_STATUS_LIST)
	outputs_status_file_handle.close()
	
except OSError:

	print ("An error occurred writing file name: ", OUTPUTS_STATUS_FILE_NAME)
	quit()

# Sleep before disabling output one
time.sleep(float(OUTPUT_ONE_SCHEDULED_ENABLE_RUNTIME_VALUE) * 60 ) 

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

CURRENT_OUTPUT_STATUS_LIST[0] = "Off\n"

try: 
	# Write the modified status to a text file
	outputs_status_file_handle = open(OUTPUTS_STATUS_FILE_NAME, 'w')
	outputs_status_file_handle.writelines(CURRENT_OUTPUT_STATUS_LIST)
	outputs_status_file_handle.close()

except OSError:

	print ("An error occurred writing file name: ", OUTPUTS_STATUS_FILE_NAME)
	quit()

print("Output one scheduled on operation complete.")


