# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot

import os
import numpy as np

thrust_set = 0.0

# save dictionary keys and values into a file
def save_settings(filename, settings):
    with open(os.path.join("GUI",filename), "w") as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")

# read dictionary keys and values from a file
def load_settings(filename):
    settings = {}

    try:
        with open(os.path.join("GUI",filename), "r") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                settings[key] = value
    except FileNotFoundError:
        print("No defaults saved")
    
    return settings


def joystick_to_setpoint(lx, ly, lt, rx, ry, rt, dt):
    def dz(v, d=0.05):
        if abs(v) < d:
            return 0.0
        return v

    lx, ly, rx, ry = map(dz, (lx, ly, rx, ry))

    roll = rx * 10.0
    pitch = -ry * 10.0
    yaw_rate = lx * 100.0

    # Trigger values usually range from -1 released to +1 fully pressed
    rt_val = (rt + 1.0) / 2.0
    lt_val = (lt + 1.0) / 2.0

    # Deadzone for triggers
    if rt_val < 0.05:
        rt_val = 0.0
    if lt_val < 0.05:
        lt_val = 0.0

    MIN_ALT = 0.0
    MAX_ALT = 1.6

    # metres per second altitude change rate
    ALT_RATE = 0.4

    # Create persistent altitude target
    if not hasattr(joystick_to_setpoint, "altitude"):
        joystick_to_setpoint.altitude = 0.0

    # Right trigger increases altitude, left trigger decreases altitude
    altitude_rate = (rt_val - lt_val) * ALT_RATE

    joystick_to_setpoint.altitude += altitude_rate * dt

    # Clamp altitude
    joystick_to_setpoint.altitude = max(
        MIN_ALT,
        min(MAX_ALT, joystick_to_setpoint.altitude)
    )

    altitude = joystick_to_setpoint.altitude

    return roll, pitch, yaw_rate, altitude

