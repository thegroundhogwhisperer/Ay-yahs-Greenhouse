# manual operation output three on
import subprocess

print("Output three manual on operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 6 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output three manual on operation complete.")


