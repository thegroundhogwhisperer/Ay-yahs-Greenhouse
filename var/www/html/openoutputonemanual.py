# manual operation output one on
import subprocess

print("Output one manual on operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output one manual on operation complete.")


