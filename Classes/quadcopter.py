# Written by Jonah Habel 2026
# Flinders University

from dataclasses import dataclass
from typing import Optional
import time
import numpy as np
from Classes.KalmanFilter import att_Kalmanfilter, pos_Kalmanfilter
from Classes.ExtendedKalmanFilter import NineDOF_EKF

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
class Velocity:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    roll: float = 0.0   
    pitch: float = 0.0
    yaw: float = 0.0


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
    def __init__(self, MASS:float, comms: str, controller, estimator, control_system):
        self.mass: float = MASS
        self.comms: str = comms
        self.controller = controller
        self.control_system = control_system
        self.estimator = estimator
        self.controls = ControlInputs() 
        self.position = Position() # coordinate readings in meters
        self.velocity = Velocity() # velocity readings in m/s
        self.attitude = Attitude() # attitude angles in degrees
        self.pitch_trim = 0.0
        self.roll_trim = 0.0
        self.loop_rate = 0.0
        self.dt = 0.033

        self.c = np.array([
            [0.5],  # linear aerodynamic damping coefficient
            [0.25]   # non-linear aerodynamic damping coefficient
        ])

        self.max_thrust = 54000 # in PWM
        self.thrust = 0.0 # in m/s^2
        self.PWM_thrust_gain = 34000 / (self.mass * 9.81) # approximate thrust gain based on gravitational force
        self.PWM_hover_thrust = 34000
        self.kd = 0.05 # drag coefficient

        # Conditions
        self.killed = False
        self.test_flight = False
        self.recording_active = False      
        self.simulation_mode = False

        self.viewer = None
        self.att_KF = None
        self.pos_KF = None
        self.EKF = None
        if self.estimator == "Kalman Filter":
            self.att_KF = att_Kalmanfilter()
            self.pos_KF = pos_Kalmanfilter()
        elif self.estimator == "Extended Kalman Filter":
            self.EKF = NineDOF_EKF()
        self.last_update_time: float = time.time()
        self.last_gyro_time = time.time()

        # System status
        self.battery_percent: Optional[int] = None # should be receieved as a percentage (e.g. 10, not 0.1)
        self.battery_voltage: Optional[float] = None # raw battery voltage (can show changes while under load)

    # centralised timestamp update function, will use provided timestamp if possible
    def _update_time(self, timestamp: Optional[float] = None):  
        self.last_update_time = timestamp if timestamp else time.time()


    # Update functions to be utilised by comms plugins, must be input with keywords (USE THESE IN PLUGINS)
    def update_position(self, *, x=None, y=None, alt=None):
        # do not update if in simulation mode
        if self.simulation_mode:
            return
        z = np.zeros((6,1))
        kf_z = np.zeros((3,1)) # separate z matrix for KF
        mask = np.zeros(6,dtype=bool)
        if x is not None:
            z[3,0] = x
            kf_z[0,0] = x
            mask[3] = True
        if y is not None:
            z[4,0] = y
            kf_z[1,0] = y
            mask[4] = True
        if alt is not None:
            z[5,0] = max(alt, 0.0)
            kf_z[2,0] = alt
            mask[5] = True
        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        # predict and correct with Kalman Filter
        if self.pos_KF is not None:
             # correct states
            self.pos_KF.correct(kf_z)

            self.position.x = self.pos_KF.x[0,0]
            self.position.y = self.pos_KF.x[1,0]
            altitude = self.pos_KF.x[2,0]

        # correct with Extended Kalman Filter
        elif self.EKF is not None:
            self.EKF.correct(z, mask)

            self.position.x = self.EKF.x[3,0]
            self.position.y = self.EKF.x[4,0]
            altitude = self.EKF.x[5,0]

        # Loco positioning system has a bias near-ground of about 0.3, this logic accounts for that smoothly
        if altitude < 0.5:
            correction = 0.3 * (1.0 - altitude / 0.5)
        else:
            correction = 0.0
        self.position.z = max(0.0, altitude - correction)

    def update_velocity(self, *, x=None, y=None, z=None, timestamp: Optional[float] = None):
        # do not update if in simulation mode
        if self.simulation_mode:
            return
        if x is not None:
            self.velocity.x = x
        if y is not None:
            self.velocity.y = y
        if z is not None:
            self.velocity.z = z

        self._update_time(timestamp)

    def update_attitude(self, *, roll=None, pitch=None, yaw=None, timestamp: Optional[float] = None):
        # do not update if in simulation mode
        if self.simulation_mode:
            return
        if roll is not None:
            self.attitude.roll = roll
        if pitch is not None:
            self.attitude.pitch = pitch
        if yaw is not None:
            self.attitude.yaw = yaw

        self._update_time(timestamp)


    def update_controls(self, *, roll=None, pitch=None, yaw_rate=None, thrust=None, z=None):
        if z is not None:
            self.controls.z = z
        # do not update if in simulation mode
        if self.simulation_mode:
            return
        u = np.zeros((4,1))
        if roll is not None:
            self.controls.roll = roll - ROLL_TRIM / self.dt
            u[1,0] = roll
        if pitch is not None:
            self.controls.pitch = -(pitch - PITCH_TRIM / self.dt)
            u[0,0] = pitch
        if yaw_rate is not None:
            self.controls.yaw_rate = yaw_rate
            u[2,0] = yaw_rate
        if thrust is not None:
            self.controls.thrust = thrust
            u[3,0] = thrust / self.PWM_thrust_gain - 9.81 # in m/s^2

        # # predict with Kalman Filter
        # if self.pos_KF is not None:
        #     self.pos_KF.predict(u, self.dt)

        # # predict with Extended Kalman Filter
        # elif self.EKF is not None:
        #     self.EKF.predict(u, self.dt)


    # predict states based on received gyro data
    def update_gyro(self, *, roll_vel=None, pitch_vel=None, yaw_vel=None):
        # do not update if in simulation mode
        if self.simulation_mode:
            return
        
        # calculate change in time
        dt = time.time() - self.last_gyro_time
        # save current time as last update time
        self.last_gyro_time = time.time()

        u = np.zeros((4,1))
        u[3,0] = self.thrust

        # fill control matrix with attitude velocities
        if roll_vel is not None:
            u[1,0] = np.deg2rad(roll_vel)
        
        if pitch_vel is not None:
            u[0,0] = np.deg2rad(pitch_vel)
        
        if yaw_vel is not None:
            u[2,0] = np.deg2rad(yaw_vel)

        u[3,0] = self.controls.thrust / self.PWM_hover_thrust # in g

        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        if self.att_KF is not None:
            u_att = np.zeros((3,1))
            u_att[0,0] = u[1,0]
            u_att[1,0] = u[0,0]
            u_att[2,0] = u[2,0]
             # predict states
            self.att_KF.predict(u_att, dt)
            # update attitudes based on predicted states
            self.update_attitude(
                roll = np.rad2deg(self.att_KF.x[0,0]),
                pitch = np.rad2deg(self.att_KF.x[1,0]),
                yaw = np.rad2deg(self.att_KF.x[2,0])
            )
                # predict with Extended Kalman Filter
        elif self.EKF is not None:
            self.EKF.predict(u, dt)
            # update attitudes based on predicted states
            self.update_attitude(
                roll = np.rad2deg(self.EKF.x[1,0]),
                pitch = np.rad2deg(self.EKF.x[0,0]),
                yaw = np.rad2deg(self.EKF.x[2,0])
            )
    

    # correct currently predicted states based on accelerometer data
    def update_acc(self, *, a_x = None, a_y = None, a_z = None):
        # do not update if in simulation mode
        if self.simulation_mode:
            return
        z = np.zeros((6,1))
        z_att = np.zeros((2,1))
        mask = np.zeros(6,dtype=bool)

        # fill measurement matrix with accelerometer readings
        z[0,0] = np.arctan2(-a_y, np.sqrt(a_x**2 + a_z**2)) - np.deg2rad(ACC_PITCH_BIAS) # update pitch
        z_att[0,0] = z[0,0]
        mask[0] = True

        z[1,0] = np.arctan2(a_x, np.sqrt(a_y**2 + a_z**2)) - np.deg2rad(ACC_ROLL_BIAS) # update roll
        z_att[1,0] = z[1,0]
        mask[1] = True

        # ADD ESTIMATOR PLUGIN HERE AS AN ELIF STATEMENT
        if self.att_KF is not None:
            # correct states
            z_att[0,0] = z[0,0]
            z_att[1,0] = z[1,0]
            self.att_KF.correct(z_att)

            # update attitudes based on corrected states
            self.update_attitude(
                roll = np.rad2deg(self.att_KF.x[0,0]),
                pitch = np.rad2deg(self.att_KF.x[1,0]),
                yaw = np.rad2deg(self.att_KF.x[2,0])
            )
        if self.EKF is not None:
            if (self.EKF.x[6,0]**2+self.EKF.x[7,0]**2) > 0.02:
                z[2,0] = np.atan2(self.EKF.x[7,0], self.EKF.x[6,0]) # update yaw
                mask[2] = True
            self.EKF.correct(z, mask)
            self.update_attitude(
                roll = np.rad2deg(self.EKF.x[1,0]),
                pitch = np.rad2deg(self.EKF.x[0,0]),
                yaw = np.rad2deg(self.EKF.x[2,0])
            )


    





