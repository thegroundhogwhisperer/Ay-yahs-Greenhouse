#!/usr/bin/perl

# Author: TheGroundHogWhisperer
# greenhousealarm.pl  
# A Perl script that:
# Uses CURL to fetch a .CSV file via http and return the last temperature value recorded.
# Evaluates if an audible alert should be generated using the spd-say text-to-speech 
# speech-dispatcher as output to the audio system if the current greenhouse temperature
# is too high or too low.
#
# Example sudo crontab -e configuration executing this script every five minutes
# */5 * * * * perl /home/pi/greenhousealarm.pl

use strict;
use warnings;

# Minimum temperature value to sound alarm
  my $MINIMUMTEMPERATUREALARM = "32";

# Maximum temperature value to sound alarm
  my $MAXIMUMTEMPERATUREALARM = "90";

# Number of audible alarm notifications
  my $NUMBEROFALARMNOTIFICATIONS = 2;

# Local copy of the remotely fetched greenhouse.csv file
  my $LOCALFILENAME = "greenhouse.csv";

# Replace the file path with a URL (e.g. http://192.168.1.118/greenhouse.csv)
  my $URLFILEPATH = "file:///home/pi/Desktop/greenhouse.csv";

# Create the curl command to fetch and store the latest greenhouse.csv from the automation system
  my @cmd = ("curl", "-o", $LOCALFILENAME, $URLFILEPATH);
     # Execute the command
     system(@cmd);

# Open the file for reading
  open(my $data, '<', $LOCALFILENAME) or die "Could not open '$LOCALFILENAME' $!\n";

# Read the entire file and set the scalar $last equal to the last line of the file
  my $last = <$data>;

# Loop through the file
  while (<$data>) { $last = $_ }

# Close the file
  close $data;

# Print the last line of the file to the console
  print "Last Record: $last\n";

# Parse out the last temperature value from the array created by using split at commas
  my @values = split /,/, $last;
  my $currentgreenhousetemperature = $values[2];

# Print the current greenhouse temperature to the console
  print "Greenhouse Temperature: $currentgreenhousetemperature\n";

# Set the temperature value to 72 degrees if the last recorded value was None
  if ( $currentgreenhousetemperature eq 'None' ) { $currentgreenhousetemperature = 72; }

# Evaluate if we should produce an audible alert using the spd-say text-to-speech command
  if ( $currentgreenhousetemperature < $MINIMUMTEMPERATUREALARM ) {

       my $alarmtemperaturedifference = $currentgreenhousetemperature - $MINIMUMTEMPERATUREALARM;

      # Create the tts command reading the current temperature alarm aloud
        @cmd = ("spd-say", "Attention! Attention! Attention! The current greenhouse temperature is: $currentgreenhousetemperature  The current minimum temperature alarm is set at: $MINIMUMTEMPERATUREALARM. That is a temperature difference of $alarmtemperaturedifference degrees. The current temperature is too low! The little plants will freeze!");


         # Execute the tts command x number of times in a loop sleeping twenty seconds between commands
           foreach (0..$NUMBEROFALARMNOTIFICATIONS) { system(@cmd); sleep(20); }

         # Print the warning alert to the console
           print "Attention! Attention! Attention! The current greenhouse temperature is: $currentgreenhousetemperature  The current minimum temperature alarm is set at: $MINIMUMTEMPERATUREALARM. That is a temperature difference of $alarmtemperaturedifference degrees. The current temperature is too low! The little plants will freeze!\n";

                                                                   }

  elsif ( $currentgreenhousetemperature > $MAXIMUMTEMPERATUREALARM ) {

          my $alarmtemperaturedifference = $currentgreenhousetemperature - $MAXIMUMTEMPERATUREALARM;

         # Create the tts command reading the current temperature alarm aloud
           @cmd = ("spd-say", "Attention! Attention! Attention! The current greenhouse temperature is: $currentgreenhousetemperature  The current maximum temperature alarm is set at: $MAXIMUMTEMPERATUREALARM. That is a temperature difference of $alarmtemperaturedifference degrees. The current temperature is too high! The little plants will cook!");

            # Execute the tts command three times in a loop sleeping twenty seconds between commands
              foreach (0..$NUMBEROFALARMNOTIFICATIONS) { system(@cmd); sleep(20); }

         # Print the warning alert to the console
           print "Attention! Attention! Attention! The current greenhouse temperature is: $currentgreenhousetemperature  The current maximum temperature alarm is set at: $MAXIMUMTEMPERATUREALARM. That is a temperature difference of $alarmtemperaturedifference degrees. The current temperature is too high! The little plants will cook!\n";

                                                                     }


