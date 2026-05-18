import os
import numpy as np

thrust_set = 0.0

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


def joystick_to_setpoint(lx, ly, lt, rx, ry, rt):
    def dz(v, d=0.05):
        if abs(v) < d:
            return 0.0
        return v

    lx, ly, rx, ry = map(dz, (lx, ly, rx, ry))

    roll = rx * 10.0
    pitch = -ry * 10.0
    yaw_rate = lx * 100.0


    # normalize triggers
    rt_val = (rt + 1) / 2
    lt_val = (lt + 1) / 2

    # combine
    throttle = rt_val - lt_val
    throttle = max(0.0, throttle)

    MIN_THRUST = 0
    MAX_THRUST = 50000

    thrust = int(MIN_THRUST + throttle * (MAX_THRUST - MIN_THRUST))


    return roll, pitch, yaw_rate, thrust


# hover logic to be run when hover mode active
def hover_logic():
    thrust = int(38000)
    roll = 0.0
    pitch = 0.0
    yaw_rate = 0.0

    return roll, pitch, yaw_rate, thrust