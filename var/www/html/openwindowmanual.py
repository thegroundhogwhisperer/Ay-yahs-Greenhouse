# manual operation of the linear actuator extension
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended

# linear actuator runtime value file name (seconds)
LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME = '/var/www/html/actuatorruntime.txt'

try: 
	global LINEAR_ACTUATOR_RUN_TIME_VALUE
	# read the current linear actuator runtime value from a file
	actuator_runtime_value_file_handle = open(LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME, 'r')
	LINEAR_ACTUATOR_RUN_TIME_VALUE = actuator_runtime_value_file_handle.readline()
	actuator_runtime_value_file_handle.close()
	print ("Read LINEAR_ACTUATOR_RUN_TIME_VALUE from file", LINEAR_ACTUATOR_RUN_TIME_VALUE)
	
except OSError:

	print ("An error occurred reading file name: ", LINEAR_ACTUATOR_RUNTIME_VALUE_FILE_NAME)
	quit()


print("Linear actuator manual extension operation starting.")

# toggle relay #2 on to extend the linear actuator
automationhat.relay.one.toggle()
time.sleep(float(LINEAR_ACTUATOR_RUN_TIME_VALUE))

# toggle relay #2 off
automationhat.relay.one.toggle()
print("Linear actuator manual extension operation complete.")


