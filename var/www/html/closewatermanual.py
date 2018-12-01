# manual operation of the solenoid valve
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

print("Solenoid valve manual open operation starting.")

# toggle relay #3 on to open the solenoid valve
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Solenoid valve manual open operation complete.")


