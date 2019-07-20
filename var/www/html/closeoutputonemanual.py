# manual operation output one off
import subprocess

print("Output one manual off operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 5 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output one manual off operation complete.")


