from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class Position:
    x: float = 0.0 # x coordinate in meters
    y: float = 0.0 # y coordinate in meters
    z: float = 0.0 # z coordinate in meters

@dataclass
class Attitude:
    roll: float = 0.0 # roll in degrees
    pitch: float = 0.0 # pitch in degrees
    yaw: float = 0.0 # yaw in degrees

class Quadcopter:
    def __init__(self, ID):
        # Device details
        self.ID: str = ID 

        # Kinematic state
        self.position = Position() # position coordinates in meters
        self.velocity = Position() # velocity in x, y, z in meters / second
        self.attitude = Attitude() # attitude angles in degrees

        # Timing
        self.last_update_time: float = time.time()

        # System status (to be integrated later)
"""       
        self.battery_voltage: Optional[float] = None
        self.battery_percent: Optional[float] = None
   #     self.flight_mode: Optional[str] = None
"""


# Centralised time update, when called will update with either current time on system or timestamp parameter
def _update_time(self, timestamp):
    self.last_update_time = timestamp if timestamp else time.time()


# Update functions to be utilised by protocol adapter, must be input with keywords
    def update_position(self, *, x=None, y=None, z=None, timestamp=None):
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if z is not None:
            self.position.z = z

        self._update_time(timestamp)

    def update_velocity(self, *, x=None, y=None, z=None, timestamp=None):
        if x is not None:
            self.velocity.x = x
        if y is not None:
            self.velocity.y = y
        if z is not None:
            self.velocity.z = z

        self._update_time(timestamp)

    def update_attitude(self, *, roll=None, pitch=None, yaw=None, timestamp=None):
        if roll is not None:
            self.attitude.roll = roll
        if pitch is not None:
            self.attitude.pitch = pitch
        if yaw is not None:
            self.attitude.yaw = yaw

        self._update_time(timestamp)