# manual operation output two off
import subprocess

print("Output two manual off operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 12 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output two manual off operation complete.")


