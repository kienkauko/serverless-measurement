#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
UID = "23iX" # Change XYZ to the UID of your Voltage/Current Bricklet 2.0

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_voltage_current_v2 import BrickletVoltageCurrentV2
import time

ipcon = IPConnection() # Create IP connection
pw = BrickletVoltageCurrentV2(UID, ipcon) # Create device object
ipcon.connect(HOST, PORT) # Connect to brickd
# Callback function for current callback
def cb_current(current):
    print("Current: " + str(current/1000.0) + " A")

# Callback function for power callback
def cb_power(power):
    print("power: " + str(power/1000.0) + " W")
    
if __name__ == "__main__":
    print("Testing of the Tinkerforge is working correctly")
    # vc = BrickletVoltageCurrentV2(UID, ipcon) # Create device object

    # ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    # Register current callback to function cb_current
    # vc.register_callback(vc.CALLBACK_CURRENT, cb_current)

    # Set period for current callback to 1s (1000ms) without a threshold
    # vc.set_current_callback_configuration(500, False, "x", 0, 0)

 # Register power callback to function cb_power
    pw.register_callback(vc.CALLBACK_POWER, cb_power)

    # Configure threshold for power "greater than 10 W"
    # with a debounce period of 1s (1000ms)
    pw.set_power_callback_configuration(1000, False, ">", 1*1000, 0)
    # while True:
    #     print("power: " + str(vc.get_power()/1000.0) + " W")
    #     time.sleep(0.1)
    
    input("Press key to exit\n") # Use raw_input() in Python 2
    ipcon.disconnect()