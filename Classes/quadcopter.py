from dataclasses import dataclass
from typing import Optional
import time
import numpy as np


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
    def __init__(self, ID: str, comms: str):
        self.ID: str = ID 
        self.comms: str = comms
        self.position = Position() # coordinate readings in meters
        self.velocity = Position() # velocity readings in m/s
        self.attitude = Attitude() # attitude angles in degrees
        # thrust array
        self.thrust = np.array([ [0.0], # total thrust
                                 [0.0], # M1 thrust
                                 [0.0], # M2 thrust
                                 [0.0], # M3 thrust
                                 [0.0], # M4 thrust

        ])

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


    # Update functions to be utilised by comms plugins, must be input with keywords (USE THESE IN PLUGINS)
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

        
    def update_thrust(self, total=None, m1=None, m2=None, m3=None, m4=None, timestamp: Optional[float] = None):
        if total is not None:
            self.thrust[0,0] = total
        if m1 is not None:
            self.thrust[1,0] = m1
        if m2 is not None:
            self.thrust[2,0] = m2
        if m3 is not None:
            self.thrust[3,0] = m3
        if m4 is not None:
            self.thrust[4,0] = m4

        self._update_time(timestamp)