from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Attitude:
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0


# quadcopter class containing generic data requirements
class Quadcopter:
    def __init__(self, ID: str):
        self.ID: str = ID 
        self.position = Position() # coordinate readings in meters
        self.velocity = Position() # velocity readings in m/s
        self.attitude = Attitude() # attitude angles in degrees
        self.last_update_time: float = time.time()

        # System status (to be integrated later)
    """       
        self.battery_voltage: Optional[float] = None
        self.battery_percent: Optional[float] = None
        self.flight_mode: Optional[str] = None
    """
    # centralised timestamp update function, will use provided timestamp if possible
    def _update_time(self, timestamp: Optional[float] = None):  
        self.last_update_time = timestamp if timestamp else time.time()


    # Update functions to be utilised by comms plugins, must be input with keywords
    def update_position(self, *, x=None, y=None, z=None, timestamp: Optional[float] = None):
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if z is not None:
            self.position.z = z

        self._update_time(timestamp)

    def update_velocity(self, *, x=None, y=None, z=None, timestamp: Optional[float] = None):
        if x is not None:
            self.velocity.x = x
        if y is not None:
            self.velocity.y = y
        if z is not None:
            self.velocity.z = z

        self._update_time(timestamp)

    def update_attitude(self, *, roll=None, pitch=None, yaw=None, timestamp: Optional[float] = None):
        if roll is not None:
            self.attitude.roll = roll
        if pitch is not None:
            self.attitude.pitch = pitch
        if yaw is not None:
            self.attitude.yaw = yaw

        self._update_time(timestamp)