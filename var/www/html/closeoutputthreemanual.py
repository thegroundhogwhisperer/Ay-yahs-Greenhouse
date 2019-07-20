# manual operation output three off
import subprocess

print("Output three manual off operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 6 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output three manual off operation complete.")


