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
##--- Date: 28th April 2019
##--- Version: 1.0
##--- Python Ver: 2.7
##--- Description: This modified python code dials out once a day at a specified time and plays an audio
##--- message on the Phone line.
##------------------------------------------

import serial
import time
import threading
import atexit
import sys
import re
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
DIAL_OUT_NUMBERS = ['1234567;', '1234567;']

# The time of day to dial out in a 0-24 hour 0-59 minute format
DIAL_OUT_HOUR = 16 # 0-23
DIAL_OUT_MINUTE = 20 # 0-59

# Path and file name of the answering machine message WAV file
AUDIO_MESSAGE_FILE_PATH = '/home/username/greenhousettsrf/greenhouseanswer.wav'

# Duration of call before disconnect in minutes
CALL_TIME_OUT_MINUTES = 3

# Delay between dialing out and the start of message playback in seconds
DIAL_OUT_PLAY_MESSAGE_DELAY_SECONDS = 8

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
# Play wav file
#=================================================================
def play_audio():
	print "Play Audio Msg - Start"

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

	time.sleep(1)

	# Play Audio File

	global disable_modem_event_listener
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

	cmd = "<DLE><ETX>" + "\r"
	analog_modem.write(cmd.encode())

	# Call Min Time Out
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

	print "Play Audio Msg - END"
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

