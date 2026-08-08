# Written by Jonah Habel 2026
# Flinders University

from dataclasses import dataclass
from typing import Optional
import time
import numpy as np
from Classes.KalmanFilter import att_Kalmanfilter, pos_Kalmanfilter

ACC_PITCH_BIAS = 0.95 # BIAS in degrees (more negative steers more forward, more positive steers more backward)
ACC_ROLL_BIAS = -0.55 # BIAS in degrees (more negative steers more right, more positive steers more left)
PITCH_TRIM = 0.0
ROLL_TRIM = 0.0

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
    z: float = 0.0


# quadcopter class containing generic data requirements
class Quadcopter:
    def __init__(self, ID: str, comms: str, controller, estimator, control_system):
        self.ID: str = ID 
        self.comms: str = comms
        self.controller = controller
        self.control_system = control_system
        self.estimator = estimator
        self.mass = 0.27
        self.controls = ControlInputs() 
        self.position = Position() # coordinate readings in meters
        self.velocity = Position() # velocity readings in m/s
        self.attitude = Attitude() # attitude angles in degrees
        self.pitch_trim = 0.0
        self.roll_trim = 0.0
        self.loop_rate = 0.0
        self.dt = 0.033

        self.max_thrust = 54000
        self.thrust = 0.0

        # Conditions
        self.killed = False
        self.test_flight = False
        self.recording_active = False      

        self.viewer = None
        if self.estimator == "Kalman Filter":
            self.att_KF = att_Kalmanfilter()
            self.pos_KF = pos_Kalmanfilter()
        else:
            self.att_KF = None
        self.last_update_time: float = time.time()

        # System status
        self.battery_percent: Optional[int] = None # should be receieved as a percentage (e.g. 10, not 0.1)
        self.battery_voltage: Optional[float] = None # raw battery voltage (can show changes while under load)

    # centralised timestamp update function, will use provided timestamp if possible
    def _update_time(self, timestamp: Optional[float] = None):  
        self.last_update_time = timestamp if timestamp else time.time()


    # Update functions to be utilised by comms plugins, must be input with keywords (USE THESE IN PLUGINS)
    def update_position(self, *, x=None, y=None, alt=None):
        u = np.zeros((3,1))
        if self.controls.thrust > 0:
            u[2,0] = 9.81 * (self.controls.thrust / 34000 - 1)
        z = np.zeros((3,1))
        if x is not None:
            z[0,0] = x
        if y is not None:
            z[1,0] = y
        if alt is not None:
            z[2,0] = alt

        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now
        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        if self.pos_KF is not None:
             # predict states
            self.pos_KF.predict(u, dt)
            self.pos_KF.correct(z)

        self.position.x = self.pos_KF.x[0,0]
        self.position.y = self.pos_KF.x[1,0]

        # Loco positioning system has a bias near-ground of about 0.3, this logic accounts for that smoothly
        z = self.pos_KF.x[2,0]
        if z < 0.5:
            correction = 0.3 * (1.0 - z / 0.5)
        else:
            correction = 0.0
        self.position.z = max(0.0, z - correction)

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


    def update_controls(self, *, roll=None, pitch=None, yaw_rate=None, thrust=None, z=None):
        if roll is not None:
            self.controls.roll = roll - ROLL_TRIM / self.dt
        if pitch is not None:
            self.controls.pitch = pitch - PITCH_TRIM / self.dt
        if yaw_rate is not None:
            self.controls.yaw_rate = yaw_rate
        if thrust is not None:
            self.controls.thrust = thrust
        if z is not None:
            self.controls.z = z

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
        if self.att_KF is not None:
             # predict states
            self.att_KF.predict(u, dt)
            # update attitudes based on predicted states
            # self.update_attitude(
            #     roll = np.rad2deg(self.att_KF.x[0,0]),
            #     pitch = np.rad2deg(self.att_KF.x[1,0]),
            #     yaw = np.rad2deg(self.att_KF.x[2,0])
            # )

    # correct currently predicted states based on accelerometer data
    def update_acc(self, *, a_x = None, a_y = None, a_z = None):
        z = np.zeros((2,1))

        # fill measurement matrix with accelerometer readings
        if a_y is not None and a_z is not None:
            z[0,0] = np.arctan2(-a_y, a_z) - np.deg2rad(ACC_ROLL_BIAS)
        if a_y is not None and a_z is not None and a_x is not None:
            z[1,0] = np.arctan2(a_x, np.sqrt(a_y*a_y + a_z*a_z)) - np.deg2rad(ACC_PITCH_BIAS)

        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        if self.att_KF is not None:
            # correct states
            self.att_KF.correct(z)

            # update attitudes based on corrected states
            self.update_attitude(
                roll = np.rad2deg(self.att_KF.x[0,0]),
                pitch = np.rad2deg(self.att_KF.x[1,0]),
                yaw = np.rad2deg(self.att_KF.x[2,0])
            )


    





