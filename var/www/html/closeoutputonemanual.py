# manual operation output one off
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

print("Output one manual off operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output one manual off operation complete.")


