# Ay-yahs-Greenhouse


# Python scripts for generating greenhouse environmental data an audio file containing text-to-speech data, RTTY data, and SSTV data content. This audio file is used as the default greeting message played via a USB modem connected to a POTS (Plain Old Telephone Service) landline.


# greenhousestatusttsrttysstvpots.py


# Requirements: 

Non-interactive network downloader (wget)

Ubuntu speech-dispatcher (spd-say)

General-purpose software audio FSK modem (minimodem)

Cross-platform command line audio manipulation utility (sox)

Python classes for generating Slow-scan Television transmissions (PySSTV)

sudo apt install python3-pip

sudo python3 -m pip install PySSTV

sudo apt install pyserial

Modem with voice support (TAD/TAM)

play_audio.py by Pradeep Singh

For more information about the play_audio.py Python code please reference this: https://github.com/pradeesi/play_audio_over_phone_line  and this:  https://iotbytes.wordpress.com/play-audio-file-on-phone-line-with-raspberry-pi/



# 
# Produces:


# Greenhouse envrionmental data as text-to-speech audio, RTTY audio, and SSTV audio as a single audio file played by play_audio.py via a modem connected to a POTS (plain old telephone service) landline.

greenhousestatusttsrttysstvpots.py is a Python script that retrieves the latest greenhouse environmental data produced by /Greenhouse/greenhouse.py in CSV format and produces text-to-speech audio output and RTTY audio output greenhousestatusttsrttysstvpots.py then retrieves an image file produced by /Greenhouse/camera.py and produces SSTV audio output. Both the CSV file and image file are retrieved using the wget application.  Text-to-speech audio is produced using the Ubuntu speech-dispatcher. RTTY audio data is produced using the minimodem application. SSTV audio data is produced using the PySSTV Puython class. Audio from the text-to-speech output, RTTY output and SSTV output are concatenated into one audio file that is played using the using the play_audio.py Python application when an incoming call is detected. 


