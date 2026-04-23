import os

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