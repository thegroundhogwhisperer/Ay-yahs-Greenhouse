# manual operation output two off
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

print("Output two manual off operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 12 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output two manual off operation starting.")


