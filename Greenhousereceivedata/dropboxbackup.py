#!/usr/bin/env python
# encoding: utf-8
#
######################################################################
## Application file name: dropboxbackuprttysstv.py		    ##
## Description: A component of Ay-yahs-Greenhouse Automation System ##
## Description: Uploads RTTY text and QSSTV images to DropBox	    ##
## Description:							    ##
## Version: 1.04						    ##
## Project Repository: https://git.io/fhhsY			    ##
## Copyright (C) 2019 The Groundhog Whisperer			    ##
######################################################################
#
# dropboxbackuprttysstv.py is a script that uploads Fldigi textout.txt files to
# a Dropbox account only after the file is N number of seconds older than the last copy uploaded.
# dropboxbackuprttysstv.py also locates and uploads the most recently saved SSTV image
# file to a Dropbox account.
#
# Executed using crontab -e
# */5 * * * * /usr/bin/python3 /home/livestream/dropboxbackuprttysstv.py
#
# Reference
#
# https://github.com/dropbox/dropbox-sdk-python/blob/master/example/back-up-and-restore/backup-and-restore-example.py
# https://gist.github.com/Keshava11/d14db1e22765e8de2670b8976f3c7efb

import time
import glob
import os
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Configure the DropBox access token value
DROPBOX_ACCESS_TOKEN_VALUE = "POPULATE_YOUR_DROPBOX_ACCESS_TOKEN_HERE"

# Location of the textout.txt file produced by FlDigi containing RTTY messages
FLDIGI_TEXT_OUT_FILE_NAME = '/home/livestream/.fldigi/talk/textout.txt'

# Local configuration file containing that last value seconds since epoch transmitted used to prevent retransmission of text data
LAST_TEXT_OUT_SECONDS_SINCE_EPOCH_VALUE_FILE_NAME = '/home/livestream/lasttextoutdropbox.txt'

# Local configuration file containing that last value image file name transmitted used to prevent retransmission of image data
LAST_IMAGE_VALUE_FILE_NAME = '/home/livestream/lastimagedropbox.txt'

# Location containing QSSTV .PNG image files
LOCATION_SSTV_IMAGE_FILES = '/home/livestream/*.png'

# Set the minimum age in seconds between RTTY text uploads
# minimum_time_in_seconds_between_textout_uploads = 60 # one minute
# minimum_time_in_seconds_between_textout_uploads = 3600 # 3600 one hour
# minimum_time_in_seconds_between_textout_uploads = 86400 # 86400 twenty-four hours
minimum_time_in_seconds_between_textout_uploads = 604800 # 604800 seven days
# minimum_time_in_seconds_between_textout_uploads = 1209600 # 1209600 fourteen days
# minimum_time_in_seconds_between_textout_uploads = 2592000 # 2592000 thirty days


# Uploads the latest N seconds old (or updated) SSTV image and Fldigi textout.txt file to Dropbox
def backup_textout_and_sstv_images_to_dropbox():

	# Establish a dropbox connection using an application token
	dbx = dropbox.Dropbox('DROPBOX_ACCESS_TOKEN_VALUE')

	# Upload the Fldigi textout.txt file
	# Define the name and path to the textout.txt file
	fldigi_textout_txt_file_name_and_path = FLDIGI_TEXT_OUT_FILE_NAME

	# Return the textout.txt files current modification time in seconds since the Unix epoch
	file_time_modification_seconds_since_unix_epoch = os.path.getmtime(fldigi_textout_txt_file_name_and_path)

	# Read the last textout.txt modification time value sent to a Dropbox account
	# Define the path and name of the text file storing the name of the last modification time of the Fldigi textout.txt file
	last_fldigi_textout_seconds_since_unix_epoch_file_name = LAST_TEXT_OUT_SECONDS_SINCE_EPOCH_VALUE_FILE_NAME
	
	# Open the file for reading
	last_last_fldigi_textout_seconds_since_unix_epoch_name_list = open(last_fldigi_textout_seconds_since_unix_epoch_file_name,'r')
	
	# Read the value of the last image file sent
	latest_fldigi_textout_seconds_since_unix_epoch_sent = last_last_fldigi_textout_seconds_since_unix_epoch_name_list.read()
	
	# Close the file
	last_last_fldigi_textout_seconds_since_unix_epoch_name_list.close()

	# Remove the path preceding the textout.txt file name   
	fldigi_textout_txt_file_name_no_path = fldigi_textout_txt_file_name_and_path.rsplit('/', 1)

	# Define the file name and prefix the file with our local second since Unix epoch time stamp
	file_name = "/RTTY/RTTY_Data_%s_%s" % (time.time(), fldigi_textout_txt_file_name_no_path[1]) 

	print ('\nCurrent modification time textout.txt file on disk:  '  + str(file_time_modification_seconds_since_unix_epoch))
	print ('\nLast modification time of the textout.txt file uploaded to a Dropbox account:  ' + latest_fldigi_textout_seconds_since_unix_epoch_sent)

	# We may only want to upload an updated textout.txt file after a specified amount of time has passed
	# Calculate the different in seconds between the current file modification time and the last modification time the file was uploaded to a Dropbox account.
	difference_between_current_textout_modification_time_and_last_uploaded = float(file_time_modification_seconds_since_unix_epoch) - float(latest_fldigi_textout_seconds_since_unix_epoch_sent)
	print ('\n\nDifference:  ' + str(difference_between_current_textout_modification_time_and_last_uploaded))

	# Compare the last record file name to the most recent file found in the folder to determine if we upload to Dropbox
	if (difference_between_current_textout_modification_time_and_last_uploaded <= minimum_time_in_seconds_between_textout_uploads):
		print ('\nTextout.txt file is not old enough to upload yet.\n')

	# Compare the last record file name to the most recent file found in the folder to determine if we upload to Dropbox
	if (difference_between_current_textout_modification_time_and_last_uploaded > minimum_time_in_seconds_between_textout_uploads):
		print ("\nThe current file modification time is greater than the minimum difference required before uploading an updated copy of the textout.txt file to a Dropbox account!\n\nWe now write the new modification time to a text file for later comparison.\n")

	# We may want to upload an updated textout.txt file after any modification has been made
	# Compare the last record file name to the most recent file found in the folder to determine if we upload to Dropbox
	# if (str(latest_fldigi_textout_seconds_since_unix_epoch_sent) != str(file_time_modification_seconds_since_unix_epoch)):
		# print ("\nThe current file modification time is different from the modification time of the last textout.txt file uploaded to a Dropbox account!\n\nWe now write the new modification time to a text file for later comparison.\n")

		# Open the text file storing the name of the last modification time of the Fldigi textout.txt file
		last_last_fldigi_textout_seconds_since_unix_epoch_name_list = open(last_fldigi_textout_seconds_since_unix_epoch_file_name,'w')
		# Update the value stored in the text file with the new file name value we are sending now
		last_last_fldigi_textout_seconds_since_unix_epoch_name_list.write(str(file_time_modification_seconds_since_unix_epoch))
		# Close the file
		last_last_fldigi_textout_seconds_since_unix_epoch_name_list.close()


		with open(fldigi_textout_txt_file_name_and_path, 'rb') as f:
			
			# We use WriteMode=overwrite to make sure that the settings in the file
			# are changed on upload
			print ("Uploading:  " + fldigi_textout_txt_file_name_and_path + " the a Dropbox account as " + file_name + "\n\n")
			
			try:
				
				dbx.files_upload(f.read(), file_name, mode=WriteMode('overwrite'))
				
			except ApiError as err:
				
				# This checks for the specific error where a user does not have
				# enough Dropbox space quota to upload this file
				if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
					sys.exit("ERROR: Cannot back up; insufficient space.")
					
				elif err.user_message_text:
					print (	err.user_message_text)
					sys.exit()
					
				else:
					print (	err)
					sys.exit()

	# Locate and upload the latest SSTV image
	# Return a list of path names for the folder containing the QSSTV image files
	list_of_sstv_image_files = glob.glob(LOCATION_SSTV_IMAGE_FILES) 

	# Return the latest image file found in the folder
	latest_sstv_image_file_and_path = max(list_of_sstv_image_files, key=os.path.getctime)

	# Define the path and name of the text file storing the name of the last SSTV image file uploaded to a Dropbox account.
	last_image_name_list_file = LAST_IMAGE_VALUE_FILE_NAME
	
	# Open the file for reading
	last_image_name_list = open(last_image_name_list_file,'r')
	
	# Read the value of the last image file sent
	latest_image_name_sent = last_image_name_list.read()
	
	# Close the file
	last_image_name_list.close()
	
	# Remove the path preceding the image file name   
	sstv_image_file_name_no_path = latest_sstv_image_file_and_path.rsplit('/', 1)

	print ('\nMost recent SSTV image file name found:  ' + latest_sstv_image_file_and_path)
	print ('\nLast SSTV image file name uploaded to a Dropbox account:  ' + latest_image_name_sent)

	# Compare the last record file name to the most recent file found in the folder to determine if we upload to Dropbox
	if (latest_sstv_image_file_and_path == latest_image_name_sent):
	   print ('\nThe SSTV image file is not new and does not need to be uploaded yet.')

	# Compare the last record file name to the most recent file found in the folder to determine if we upload to Dropbox
	if (latest_sstv_image_file_and_path != latest_image_name_sent):
		print ("\n\nThe most recent SSTV image file name found is different from the last SSTV image file name uploaded to a Dropbox account.\n")
		print ('\n\nWe send now and record the file name for later comparison.')
		
		# Open the text file storing the name of the last image sent for writing
		last_image_name_list = open(last_image_name_list_file,'w')
		
		# Update the value stored in the text file with the new file name value we are sending now
		last_image_name_list.write(latest_sstv_image_file_and_path)
		
		# Close the file
		last_image_name_list.close()

		# Define the file name and prefix the file with our local second since Unix epoch time stamp
		file_name = "/SSTV/SSTV_Image_%s_%s" % (time.time(), sstv_image_file_name_no_path[1])

		with open(latest_sstv_image_file_and_path, 'rb') as f:
			
			# We use WriteMode=overwrite to make sure that the settings in the file
			# are changed on upload
			print ("Uploading:  " + latest_sstv_image_file_and_path + " to a Dropbox account as:  " + file_name + "...")

			try:
				
				dbx.files_upload(f.read(), file_name, mode=WriteMode('overwrite'))
				
			except ApiError as err:
				
				# This checks for the specific error where a user doesn't have
				# enough Dropbox space quota to upload this file
				if (err.error.is_path() and
						err.error.get_path().reason.is_insufficient_space()):
					sys.exit("ERROR: Cannot back up; insufficient space.")
					
				elif err.user_message_text:
					print (	err.user_message_text)
					sys.exit()
					
				else:
					print (	err)
					sys.exit()

# Call the main subroutine
backup_textout_and_sstv_images_to_dropbox()

