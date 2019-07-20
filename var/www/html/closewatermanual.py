# manual operation of the solenoid valve
import subprocess

print("\nSolenoid valve manual close operation starting. \n")

# toggle relay #3 on to close the solenoid valve
pigsGPIOCommandLine = ["/usr/bin/pigs", "w 16 0"]
p = subprocess.Popen(pigsGPIOCommandLine)

print("Solenoid valve manual close operation complete. \n")


