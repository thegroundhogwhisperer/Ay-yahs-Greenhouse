# manual operation output two on
import subprocess

print("Output two manual on operation starting.")

pigsGPIOCommandLine = ["/usr/bin/pigs", "w 12 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Output two manual on operation complete.")


