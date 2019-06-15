##------------------------------------------
##--- Author: Pradeep Singh
##--- Blog: https://iotbytes.wordpress.com/play-audio-file-on-phone-line-with-raspberry-pi/
##--- Date: 24th June 2018
##--- Version: 1.0
##--- Python Ver: 2.7
##--- Description: This python code will pick an incomming call and play an audio msg on the Phone line.
##------------------------------------------
##--- Modified: The Groundhog Whisperer
##--- GitHub: https://github.com/thegroundhogwhisperer/Ay-yahs-Greenhouse
##--- Date: 14th June 2019
##--- Version: 1.0
##--- Python Ver: 2.7
##--- Description: This modified python code dials out once a day at a specified time and plays an audio msg on the phone line.
##--- Description: This modified python code will pick up an incoming call and play an audio msg on the phone line while
##--- Description: parsing DTMF input for a specific sequence match and will fetch a remote URL with the intent to trigger
##--- Description: an event. (e.g. Open or close the greenhouse window, turn on or off the light, etc.)
##------------------------------------------

import serial
import time
import threading
import atexit
import sys
import re
import urllib2
import wave

analog_modem = serial.Serial()
analog_modem.port = "/dev/ttyACM0"
analog_modem.baudrate = 57600 # 57600
analog_modem.bytesize = serial.EIGHTBITS # number of bits per bytes
analog_modem.parity = serial.PARITY_NONE # set parity check: no parity
analog_modem.stopbits = serial.STOPBITS_ONE # number of stop bits
analog_modem.timeout = 3            # non-block read
analog_modem.xonxoff = False     # disable software flow control
analog_modem.rtscts = False     # disable hardware (RTS/CTS) flow control
analog_modem.dsrdtr = False      # disable hardware (DSR/DTR) flow control
analog_modem.writeTimeout = 3     # timeout for write

# Used in global event listener
disable_modem_event_listener = True

RINGS_BEFORE_AUTO_ANSWER = 4

# Phone numbers to dial out and play the audio message 
DIAL_OUT_NUMBERS = ['1234567;', '1234567;', '1234567;']

# The time of day to dial out in a 0-24 hour 0-59 minute format
DIAL_OUT_HOUR = 16 # 0-23
DIAL_OUT_MINUTE = 20 # 0-59

# Path and file name of the answering machine message WAV file
AUDIO_MESSAGE_FILE_PATH = '/home/username/greenhousettsrf/greenhouseanswer.wav'

# Duration of call before disconnect in minutes (while dialing out)
CALL_TIME_OUT_MINUTES = 3

# Delay between dialing out and the start of message playback in seconds (while dialing out)
DIAL_OUT_PLAY_MESSAGE_DELAY_SECONDS = 5

# DTMF numerical input number to remote control function
DTMF_CODE_FUNCTION_ZERO = ['4','2','#','0']  # Enter DTMF tones 4 2 # 0 to execute a fetch of list item 0 (fan on)
DTMF_CODE_FUNCTION_ONE = ['4','2','#','1']  # Enter DTMF tones 4 2 # 1 to execute a fetch of list item 1 (fan off)
DTMF_CODE_FUNCTION_TWO = ['4','2','#','2']  # Enter DTMF tones 4 2 # 2 to execute a fetch of list item 2 (light on)
DTMF_CODE_FUNCTION_THREE = ['4','2','#','3']  # Enter DTMF tones 4 2 # 3 to execute a fetch of list item 0 (light off)
DTMF_CODE_FUNCTION_FOUR = ['4','2','#','4']
DTMF_CODE_FUNCTION_FIVE = ['4','2','#','5']
DTMF_CODE_FUNCTION_SIX = ['4','2','#','6']
DTMF_CODE_FUNCTION_SEVEN = ['4','2','#','7']
DTMF_CODE_FUNCTION_EIGHT = ['4','2','#','8']
DTMF_CODE_FUNCTION_NINE = ['4','2','#','9']

# DTMF numerical input number to remote control function list
# 0/1 Turn on/off the greenhouse fan
# 2/3 Turn on/off the greenhouse light
# 4/5 Turn on/off output three
# 6/7 Open/close the water solenoid valve
# 8/9 Open/close the window
REMOTE_CONTROL_URLS = ['http://192.168.1.118/openoutputonemanual.php',
			'http://192.168.1.118/closeoutputonemanual.php',
			'http://192.168.1.118/openoutputtwomanual.php',
			'http://192.168.1.118/closeoutputtwomanual.php',
			'http://192.168.1.118/openoutputthreemanual.php',
			'http://192.168.1.118/closeoutputthreemanual.php',
			'http://192.168.1.118/openwatermanual.php',
			'http://192.168.1.118/closewatermanual.php',
			'http://192.168.1.118/openwindowmanual.php',
			'http://192.168.1.118/closewindowmanual.php']

# Timeout in seconds before urllib2 fails to fetch the remote URL
URL_FETCH_TIMEOUT_SECONDS = 3

# DTMF input timeout in seconds after the audio message is played 
DTMF_INPUT_TIMEOUT_SECONDS = 10

# Define the list that holds the temporary DTMF input values during the play_audio() function
LIST_INDIVIDUAL_DTMF_DIGITS = []

#=================================================================
# Initialize Modem
#=================================================================
def init_modem_settings():
	# Open Serial Port
	try:
		analog_modem.open()
	except:
		print "Error: Unable to open the Serial Port."
		sys.exit()

	# Initialize
	try:
		analog_modem.flushInput()
		analog_modem.flushOutput()

		# Test Modem connection, using basic AT command.
		if not exec_AT_cmd("AT"):
			print "Error: Unable to access the Modem"

		# Reset to factory default.
		if not exec_AT_cmd("ATZ"):
			print "Error: Unable reset to factory default"			

                # Enable formatted caller report.
                if not exec_AT_cmd("ATH0"):
                        print "Error: Failed to hangup/close line."

                # Enable formatted caller report.
                if not exec_AT_cmd("ATH"):
                        print "Error: Failed to hangup/close line."

		# Display result codes in verbose form 	
		if not exec_AT_cmd("ATV1"):
			print "Error: Unable set response in verbose form"	

		# Enable Command Echo Mode.
		if not exec_AT_cmd("ATE1"):
			print "Error: Failed to enable Command Echo Mode"		

		# Enable formatted caller report.
		if not exec_AT_cmd("AT+VCID=1"):
			print "Error: Failed to enable formatted caller report."

		analog_modem.flushInput()
		analog_modem.flushOutput()

	except:
		print "Error: unable to Initialize the Modem"
		sys.exit()
#=================================================================



#=================================================================
# Execute AT Commands on the Modem
#=================================================================
def exec_AT_cmd(modem_AT_cmd):
	try:
		global disable_modem_event_listener
		disable_modem_event_listener = True

		cmd = modem_AT_cmd + "\r"
		analog_modem.write(cmd.encode())

		modem_response = analog_modem.readline()
		modem_response = modem_response + analog_modem.readline()

		print modem_response

		disable_modem_event_listener = False

		if ((modem_AT_cmd == "AT+VTX") or (modem_AT_cmd == "AT+VRX")) and ("CONNECT" in modem_response):
			# modem in TAD mode
			return True
		elif "OK" in modem_response:
			# Successful command execution
			return True
		else:
			# Failed command execution
			return False

	except:
		disable_modem_event_listener = False
		print "Error: unable to write AT command to the modem..."
		return()
#=================================================================



#=================================================================
# Recover Serial Port
#=================================================================
def recover_from_error():
	try:
		exec_AT_cmd("ATH")
	except:
		pass

	analog_modem.close()
	init_modem_settings()

	try:
		analog_modem.close()
	except:
		pass

	try:
		init_modem_settings()
	except:
		pass

	try:
		exec_AT_cmd("ATH")
	except:
		pass

#=================================================================

#=================================================================
# Read DTMF Digits
#=================================================================
def dtmf_digits(modem_data):
	#print "modem data", modem_data
	remote_command_number_option = None
	digit_list = re.findall('/(.+?)~', modem_data)
	#print "digit_list", digit_list

	for d in digit_list:

		print "\nNew Event: DTMF Digit Detected: " + d[1]
		LIST_INDIVIDUAL_DTMF_DIGITS.append(str(d[1]))
		#print "List is", LIST_INDIVIDUAL_DTMF_DIGITS

        #print "All DTMF tones detected", LIST_INDIVIDUAL_DTMF_DIGITS

	#print "Comparing: ", DTMF_CODE_FUNCTION_ZERO
	#print "Against: ", LIST_INDIVIDUAL_DTMF_DIGITS

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_ZERO:
		remote_command_number_option = 0

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_ONE:
		remote_command_number_option = 1

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_TWO:
		remote_command_number_option = 2

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_THREE:
		remote_command_number_option = 3

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_FOUR:
		remote_command_number_option = 4

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_FIVE:
		remote_command_number_option = 5

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_SIX:
		remote_command_number_option = 6

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_SEVEN:
		remote_command_number_option = 7

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_EIGHT:
		remote_command_number_option = 8

	if LIST_INDIVIDUAL_DTMF_DIGITS == DTMF_CODE_FUNCTION_NINE:
		remote_command_number_option = 9

	if remote_command_number_option is not None:

		print "Valid DTMF control code matched!"
		print "Fetching URL: ", REMOTE_CONTROL_URLS[remote_command_number_option]
		remote_control_command_request_url = urllib2.Request(REMOTE_CONTROL_URLS[remote_command_number_option])

		try: 
			response_control_command = urllib2.urlopen(remote_control_command_request_url, timeout = URL_FETCH_TIMEOUT_SECONDS)
			object_containing_the_output_response_page = response_control_command.read()
			print "URL fetch results: ", object_containing_the_output_response_page

		except urllib2.URLError as e:
			print e.reason   
	else:
		print "No DTMF control code matched."
#=================================================================





#=================================================================
# Play wav file
#=================================================================
def play_audio():
	print "Play Audio Msg - Start"

	# Enter Voice Mode
	if not exec_AT_cmd("AT+FCLASS=8"):
		print "Error: Failed to put modem into voice mode."
		return

	# Enable silence detection on a noisy line with a wait time of five seconds
	if not exec_AT_cmd("AT+VSD=129,50"):
		print "Error: Failed to enable silence detection."
		return

	# Compression Method and Sampling Rate Specifications
	# Compression Method: 8-bit linear / Sampling Rate: 8000MHz
	if not exec_AT_cmd("AT+VSM=128,8000"):
		print "Error: Failed to set compression method and sampling rate specifications."
		return

	# Put modem into TAD Mode
	if not exec_AT_cmd("AT+VLS=1"):
		print "Error: Unable put modem into TAD mode."
		return

	# Put modem into TAD Mode
	if not exec_AT_cmd("AT+VTX"):
		print "Error: Unable put modem into TAD mode."
		return

	time.sleep(1)

	# Play Audio File

	global disable_modem_event_listener
	global LIST_INDIVIDUAL_DTMF_DIGITS
	disable_modem_event_listener = True

	wf = wave.open(AUDIO_MESSAGE_FILE_PATH,'rb')
	chunk = 1024

	data = wf.readframes(chunk)
	while data != '':
		analog_modem.write(data)
		data = wf.readframes(chunk)
		# You may need to change this sleep interval to smooth-out the audio
		time.sleep(.12)
	wf.close()

        #analog_modem.flushInput()
	#analog_modem.flushOutput()
	
	try:
		data_buffer = ""
		
		# Call Min Time Out
		timeout = time.time() + DTMF_INPUT_TIMEOUT_SECONDS 
		print "Call timeout: ", timeout

		while 1:
			# Read data from the Modem
			data_buffer = data_buffer + analog_modem.read()

			# Check if <DLE>b is in the stream
			if ((chr(16)+chr(98)) in data_buffer):
				print "\nNew Event: Busy Tone... (Call will be disconnected)"
				break

			# Check if <DLE>s is in the stream
			if ((chr(16)+chr(115)) in data_buffer):
				print "\nNew Event: Silence Detected... (Call will be disconnected)"
				# My USB modem does produce a Silence Detected notification... :(
				#break
				pass

			# Check if <DLE><ETX> is in the stream
			if (("<DLE><ETX>").encode() in data_buffer):
				print "\nNew Event: <DLE><ETX> Char Recieved... (Call will be disconnected)"
				break

			# Parse DTMF Digits, if found in the Modem Data
			if len(re.findall('/(.+?)~', data_buffer)) > 0:
				dtmf_digits(data_buffer)
				data_buffer = ""

			# Disconnect the call if the DTMF input time limit is reached
			print "Time remaining: ", timeout - time.time()
			if time.time() > timeout:
				print "DTMF input time limit reached... (Call will be disconnected)"
				# Empty the list of DTMF digits input during this call
				LIST_INDIVIDUAL_DTMF_DIGITS = None
				break

		data_buffer = ""
		LIST_INDIVIDUAL_DTMF_DIGITS = []

	        analog_modem.flushInput()
		analog_modem.flushOutput()

		# Hangup the Call
		if not exec_AT_cmd("ATH0"):
			print "Error: Unable to hang-up the call"
		else:
			print "\nAction: Call Terminated..."

		# Try really hard to Hangup the Call
		if not exec_AT_cmd("ATH"):
			print "Error: Unable to hang-up the call"

			try:
				analog_modem.close()
			except:
				pass
			try:
				init_modem_settings()
				cmd = "ATH" + "\r"
				analog_modem.write(cmd.encode())		
			except:
				pass
		else:
			print "\nAction: Call Terminated..."

		return

	finally:
		# Enable global event listener
		disable_modem_event_listener = False
		print "-------------------------------------------" 

	print "Play Audio Msg - END"
	# Empty the list of DTMF digits input during this call (probably do not need the next line)
	LIST_INDIVIDUAL_DTMF_DIGITS = []
	return
#=================================================================


#=================================================================
# Dial out and play wav file
#=================================================================
def dial_out_play_audio(number_to_dial):
	print "Dialing Out Playing Audio Msg - Start"

	# Try to recover the serial port
	recover_from_error()

	# Enable speaker always on and maximum volume
	if not exec_AT_cmd("ATZ"):
		print "Error: Unable to initilized the modem."
		return

	# Enable speaker always on and maximum volume
	if not exec_AT_cmd("ATM1L3"):
		print "Error: Unable to enable speaker aways on and volume maximum."
		return

	# Disable dial tone detection
	if not exec_AT_cmd("ATX3"):
		print "Error: Unable to disable dial tone detection."
		return

	# Disable carrier detection
	if not exec_AT_cmd("AT&C0"):
		print "Error: Unable to disable carrier detection."
		return

	# Dial out
        attention_dial_tone_command = "ATDT" + str(number_to_dial)

	try:
		exec_AT_cmd(attention_dial_tone_command)
	except:
		pass

        # Amount of time to wait after ATDT dialing out to not interupt and get a NO CARRIER
	time.sleep(5)

	# Enter Voice Mode
	if not exec_AT_cmd("AT+FCLASS=8"):
		print "Error: Failed to put modem into voice mode."
		return

	# Compression Method and Sampling Rate Specifications
	# Compression Method: 8-bit linear / Sampling Rate: 8000MHz
	if not exec_AT_cmd("AT+VSM=128,8000"):
		print "Error: Failed to set compression method and sampling rate specifications."
		return

	# Put modem into TAD Mode
	if not exec_AT_cmd("AT+VLS=1"):
		print "Error: Unable put modem into TAD mode."
		return

	# Put modem into TAD Mode
	if not exec_AT_cmd("AT+VTX"):
		print "Error: Unable put modem into TAD mode."
		return

	# Play Audio File
	global disable_modem_event_listener
	disable_modem_event_listener = True

	wf = wave.open(AUDIO_MESSAGE_FILE_PATH,'rb')
	chunk = 1024

        # Amount of time to wait for an answering before playing the audio message
	time.sleep(DIAL_OUT_PLAY_MESSAGE_DELAY_SECONDS)

	data = wf.readframes(chunk)
	while data != '':
		analog_modem.write(data)
		data = wf.readframes(chunk)
		# You may need to change this sleep interval to smooth-out the audio
		time.sleep(.12)
	wf.close()

        #analog_modem.flushInput()
	#analog_modem.flushOutput()

	cmd = "<DLE><ETX>" + "\r"
	analog_modem.write(cmd.encode())

	# 5 Min Time Out
	timeout = time.time() + 60*CALL_TIME_OUT_MINUTES 
	while 1:
		modem_data = analog_modem.readline()
		if "OK" in modem_data:
			break
		if time.time() > timeout:
			break

	disable_modem_event_listener = False

	cmd = "ATH" + "\r"
	analog_modem.write(cmd.encode())

	print "Dial Out Play Audio Msg - END"
	return
#=================================================================



#=================================================================
# Modem Data Listener
#=================================================================
def read_data():
	global disable_modem_event_listener
	ring_data = ""

	while 1:
## Here         play_audio()

                result = time.localtime()
		element_counter = 0
                if result.tm_hour == DIAL_OUT_HOUR and result.tm_min == DIAL_OUT_MINUTE:
                    print "Time to dial out and play an audio file."
		    # Find the total count of phone numbers to dial
		    total_numbers_to_dial = len(DIAL_OUT_NUMBERS)

		    # Loop through the list dialing each elements value
		    while element_counter < len(DIAL_OUT_NUMBERS):
			print "Calling", DIAL_OUT_NUMBERS[element_counter]
			number_to_dial = DIAL_OUT_NUMBERS[element_counter]
                        dial_out_play_audio(number_to_dial)
			# Wait for the call to finish before calling the thread again
			time.sleep(CALL_TIME_OUT_MINUTES)
			element_counter += 1

		if not disable_modem_event_listener:
			modem_data = analog_modem.readline()
			if modem_data != "":
				print modem_data

				if "b" in modem_data.strip(chr(16)):
					print "b in modem data"
					print "b count:"
					print ((modem_data.strip(chr(16))).count("b"))
					print "total length:"
					print len(modem_data.strip(chr(16)))
					print modem_data

					if ((modem_data.strip(chr(16))).count("b")) == len(modem_data.strip(chr(16))):
						print "all Bs in mode data"
						#Terminate the call
						if not exec_AT_cmd("ATH"):
							print "Error: Busy Tone - Failed to terminate the call"
							print "Trying to revoer the serial port"
							recover_from_error()
						else:
							print "Busy Tone: Call Terminated"

				if "s" == modem_data.strip(chr(16)):
					#Terminate the call
					if not exec_AT_cmd("ATH"):
						print "Error: Silence - Failed to terminate the call"
						print "Trying to recover the serial port"
						recover_from_error()
					else:
						print "Silence: Call Terminate"

				if ("RING" in modem_data) or ("DATE" in modem_data) or ("TIME" in modem_data) or ("NMBR" in modem_data):
					if "RING" in modem_data.strip(chr(16)):
						ring_data = ring_data + modem_data
						ring_count = ring_data.count("RING")
						if ring_count == 1:
							pass
							print modem_data
						elif ring_count == RINGS_BEFORE_AUTO_ANSWER:
							ring_data = ""
							play_audio()
							# Empty the list of DTMF digits input during this call
							LIST_INDIVIDUAL_DTMF_DIGITS = None							
#=================================================================



#=================================================================
# Close the Serial Port
#=================================================================
def close_modem_port():
	try:
		exec_AT_cmd("ATH")
	except:
		pass

	try:
		if analog_modem.isOpen():
			analog_modem.close()
			print ("Serial Port closed...")
	except:
		print "Error: Unable to close the Serial Port."
		sys.exit()
#=================================================================


init_modem_settings()

#Start a new thread to listen to modem data 
data_listener_thread = threading.Thread(target=read_data)
data_listener_thread.start()



# Close the Modem Port when the program terminates
atexit.register(close_modem_port)

