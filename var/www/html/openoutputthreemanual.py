# manual operation output two on
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended
import subprocess

print("Output two manual on operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 6 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output two manual on operation complete.")


