# manual operation of the solenoid valve
import subprocess

print("Solenoid valve manual open operation starting.")

# toggle relay #3 on to open the solenoid valve
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 1"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Solenoid valve manual open operation complete.")


