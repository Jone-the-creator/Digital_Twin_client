# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot
# recorder.py
# -- defines the recorder worker class used for recording data --

from PySide6.QtCore import ( 
    QObject, Signal, QThread
)

import time, csv, os
import numpy as np
from datetime import datetime

# this worker class will be ran as a separate thread so that the recording
# can happen in the background
class RecorderWorker(QObject):
    finished = Signal()

    def __init__(self, quadcopter, observer):
        super().__init__()
        self.running = False
        self.quadcopter = quadcopter
        self.obs = observer

    def start(self):
        self.running = True

        # adds logged data to /Data folder
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "Data")
        os.makedirs(data_dir, exist_ok=True)

        # creates a timestamp for the filename at the time of recording start
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(data_dir, f"recording_{timestamp}.csv")


        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "thrust", "velocity", "yaw", "pitch", "roll", "battery", "x", "y", "z", "yaw obs", "pitch obs", "roll obs", "x obs", "y obs", "z obs",  "loop rate (Hz)", "target altitude (m)"])
            start_time = time.perf_counter()
            while self.running and not QThread.currentThread().isInterruptionRequested():
                #update this function when new variables desired
                writer.writerow([
                    round(time.perf_counter() - start_time, 3),
                    self.quadcopter.controls.thrust,
                    self.quadcopter.velocity.z,
                    self.quadcopter.attitude.yaw,
                    self.quadcopter.attitude.pitch,
                    self.quadcopter.attitude.roll,
                    self.quadcopter.battery_percent,
                    self.quadcopter.position.x,
                    self.quadcopter.position.y,
                    self.quadcopter.position.z,
                    np.rad2deg(self.obs.x[8,0]),
                    np.rad2deg(self.obs.x[7,0]),
                    np.rad2deg(self.obs.x[6,0]),
                    self.obs.x[0,0],
                    self.obs.x[1,0],
                    self.obs.x[2,0],
                    self.quadcopter.loop_rate,
                    self.quadcopter.controls.z
                ])

                f.flush()
                QThread.msleep((1/self.quadcopter.recording_rate) * 1000)  # Adjustable

        self.finished.emit()

    # this function will stop recording
    def stop(self):
        self.running = False
