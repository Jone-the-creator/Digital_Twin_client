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
from datetime import datetime

# this worker class will be ran as a separate thread so that the recording
# can happen in the background
class RecorderWorker(QObject):
    finished = Signal()

    def __init__(self, quadcopter):
        super().__init__()
        self.running = False
        self.quadcopter = quadcopter

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
            writer.writerow(["time (s)", "yaw", "pitch", "roll", "battery", "altitude (m)", "loop rate (Hz)", "target altitude (m)"])
            start_time = time.time()
            while self.running and not QThread.currentThread().isInterruptionRequested():
                #update this function when new variables desired
                writer.writerow([
                    round(time.time() - start_time, 3),
                    self.quadcopter.attitude.yaw,
                    self.quadcopter.attitude.pitch,
                    self.quadcopter.attitude.roll,
                    self.quadcopter.battery_percent,
                    self.quadcopter.position.z,
                    self.quadcopter.loop_rate,
                    self.quadcopter.controls.z
                ])

                f.flush()
                QThread.msleep(50)  # 20Hz

        self.finished.emit()

    # this function will stop recording
    def stop(self):
        self.running = False
