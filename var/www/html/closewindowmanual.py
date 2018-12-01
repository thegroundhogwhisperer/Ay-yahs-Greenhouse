# manual operation of the linear actuator retraction
import time
import automationhat
time.sleep(0.1) # short pause after ads1015 class creation recommended

# this actuators stroke is 406.4 mm at 10 mm per second
# wait 40.6 seconds to close the window
linearActuatorRunTime = 40.6

print("Linear actuator manual retraction operation starting.")

# toggle relay #2 on to extend the linear actuator
automationhat.relay.two.toggle()
time.sleep(linearActuatorRunTime)

# toggle relay #2 off
automationhat.relay.two.toggle()
print("Linear actuator manual retraction operation complete.")


