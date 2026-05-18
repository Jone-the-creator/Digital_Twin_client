from dataclasses import dataclass
from typing import Optional
import time
import numpy as np
from Classes.KalmanFilter import Kalmanfilter


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

@dataclass
class ControlInputs:
    roll: float = 0.0
    pitch: float = 0.0
    yaw_rate: float = 0.0
    thrust: float = 0.0


# quadcopter class containing generic data requirements
class Quadcopter:
    def __init__(self, ID: str, comms: str, controller, estimator, control_system):
        self.ID: str = ID 
        self.comms: str = comms
        self.controller = controller
        self.control_system = control_system
        self.estimator = estimator
        self.controls = ControlInputs() 
        self.position = Position() # coordinate readings in meters
        self.velocity = Position() # velocity readings in m/s
        self.attitude = Attitude() # attitude angles in degrees
        self.thrust = 0.0
        self.killed = False
        if self.estimator == "Kalman Filter":
            self.KF = Kalmanfilter()
        else:
            self.KF = None
        self.last_update_time: float = time.time()

        # System status
        self.battery_percent: Optional[int] = None # should be receieved as a percentage (e.g. 10, not 0.1)
        self.battery_voltage: Optional[float] = None # raw battery voltage (can show changes while under load)

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


    def update_controls(self, *, roll=None, pitch=None, yaw_rate=None, thrust=None):
        if roll is not None:
            self.controls.roll = roll
        if pitch is not None:
            self.controls.pitch = pitch
        if yaw_rate is not None:
            self.controls.yaw_rate = yaw_rate
        if thrust is not None:
            self.controls.thrust = thrust

    # predict states based on received gyro data
    def update_gyro(self, *, roll_vel=None, pitch_vel=None, yaw_vel=None):
        # calculate change in time
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        u = np.zeros((3,1))

        # fill control matrix with attitude velocities
        if roll_vel is not None:
            u[0,0] = np.deg2rad(roll_vel)
        
        if pitch_vel is not None:
            u[1,0] = np.deg2rad(pitch_vel)
        
        if yaw_vel is not None:
            u[2,0] = np.deg2rad(yaw_vel)

        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        if self.KF is not None:
             # predict states
            self.KF.predict(u, dt)

            # update attitudes based on predicted states
            self.update_attitude(
                roll = np.rad2deg(self.KF.x[0,0]),
                pitch = np.rad2deg(self.KF.x[1,0]),
                yaw = np.rad2deg(self.KF.x[2,0])
            )

    # correct currently predicted states based on accelerometer data
    def update_acc(self, *, a_x = None, a_y = None):
        z = np.zeros((2,1))

        # fill measurement matrix with accelerometer readings
        if a_x is not None:
            z[1,0] = a_x
        if a_y is not None:
            z[0,0] = -a_y

        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        if self.KF is not None:
            # correct states
            self.KF.correct(z)

            # update attitudes based on corrected states
            self.update_attitude(
                roll = np.rad2deg(self.KF.x[0,0]),
                pitch = np.rad2deg(self.KF.x[1,0]),
                yaw = np.rad2deg(self.KF.x[2,0])
            )






