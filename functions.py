import os
import pygame

# save dictionary keys and values into a file
def save_settings(filename, settings):
    with open(os.path.join("cache",filename), "w") as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")

# read dictionary keys and values from a file
def load_settings(filename):
    settings = {}

    try:
        with open(os.path.join("cache",filename), "r") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                settings[key] = value
    except FileNotFoundError:
        print("No defaults saved")
    
    return settings

def joystick_to_setpoint(lx, ly, rx, ry):
    # Deadzone
    def dz(v, d=0.05):
        return 0 if abs(v) < d else v

    lx, ly, rx, ry = map(dz, (lx, ly, rx, ry))

    roll = rx * 10.0          # degrees
    pitch = -ry * 10.0        # invert Y
    yaw_rate = lx * 50.0      # deg/s

    thrust = int((1 - ly) * 30000)  # scale & invert

    thrust = max(0, min(thrust, 35000))

    return roll, pitch, yaw_rate, thrust