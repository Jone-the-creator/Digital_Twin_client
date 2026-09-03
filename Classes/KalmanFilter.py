# Written by Jonah Habel 2026
# Flinders University
#
# KalmanFilter.py
# -- defines the kalman filter classes for attitude and position data --

import numpy as np

# only good for attitudes up to 45 degrees, numpy does algebra in radians
class att_Kalmanfilter():
    def __init__(self):
        # control noise
        self.Q = np.array([
            [0.25, 0, 0],
            [0, 0.25, 0],
            [0, 0, 0.025]
        ])
        # measurement noise
        self.R = np.array([
            [0.025, 0],
            [0, 0.025],
        ])
        # initial state
        self.x = np.zeros((3,1)) 

        # initialise covariance
        self.P = np.array([
            [0.0001, 0, 0],
            [0, 0.0001, 0],
            [0, 0, 0.06]
        ])
    
    # prediction step based on previous state and control
    def predict(self, u, dt):
        # state transition matrix
        F = np.eye(3)

        # control matrix
        G = np.eye(3) * dt
        
        # update state prediction
        self.x = F @ self.x + G @ u

        # update covariance
        self.P = F @ self.P @ F.T + self.Q

        # correction step based on predicted state and measurements, z is [a_y, a_x]
    def correct(self, z):
        # measurement matrix
        H = np.array([
            [-1, 0, 0],
            [0, 1, 0]
        ])

        # calculate Kalman gain
        K = self.P @ H.T @ np.linalg.pinv(H @ self.P @ H.T + self.R)

        # update state estimate
        self.x = self.x + K @ (z - H @ self.x)

        # update covariance
        self.P = (np.eye(3) - K @ H) @ self.P

class pos_Kalmanfilter():
    def __init__(self, quadcopter):
        self.quad = quadcopter
        # control noise, ALTITUDE TUNED
        self.Q = np.array([
            [0.175, 0, 0],
            [0, 0.175, 0],
            [0, 0, 0.05]
        ])
        # measurement noise, ALTITUDE TUNED
        self.R = np.array([
            [0.05, 0, 0],
            [0, 0.05, 0],
            [0, 0, 0.5]
        ])
        # initial state (0.65, 0.75, 0.0 for home - x, y, 0.0 for FFoF)
        self.x = np.array([
            [0.65],
            [0.75],
            [0.0]
        ])

        # initialise covariance, ALTITUDE TUNED
        self.P = np.array([
            [0.025, 0, 0],
            [0, 0.025, 0],
            [0, 0, 0.01]
        ])

    def _f(self, dt, x, u):
        Thrust = u[3,0] / self.quad.PWM_thrust_gain
        yaw = self.quad.attitude.yaw
        roll = self.quad.attitude.roll
        pitch = self.quad.attitude.pitch
        x[0,0] += x[0,0] - Thrust/self.quad.mass * (np.cos(yaw)*np.sin(pitch)*np.cos(roll) + np.sin(yaw)*np.sin(roll)) * dt
        x[1,0] += x[1,0] - Thrust/self.quad.mass * (np.sin(yaw)*np.sin(pitch)*np.cos(roll) - np.cos(yaw)*np.sin(roll)) * dt
        x[2,0] += x[2,0] + (Thrust/self.quad.mass * (np.sin(pitch)*np.cos(roll)) - 9.81) * dt
    
    # prediction step based on previous state and control, u for altitude is g * (T/Thover - 1)
    def predict(self, u, dt):
        Thrust = u[3,0] / self.quad.PWM_thrust_gain
        yaw = self.quad.attitude.yaw
        roll = self.quad.attitude.roll
        pitch = self.quad.attitude.pitch
        mu = self.x.copy()
        # state transition matrix
        F = np.eye(3)

        # control matrix
        G = np.array((
            [-Thrust/self.quad.mass * (-np.cos(yaw)*np.sin(pitch)*np.cos(roll) + np.sin(yaw)*np.cos(roll)) * dt, -Thrust/self.quad.mass * (np.cos(yaw)*np.cos(pitch)*np.cos(roll) + np.sin(yaw)*np.sin(roll)) * dt, -Thrust/self.quad.mass * (-np.sin(yaw)*np.sin(pitch)*np.cos(roll) + np.cos(yaw)*np.sin(roll)) * dt, -1/self.quad.mass * (np.cos(yaw)*np.sin(pitch)*np.cos(roll) + np.sin(yaw)*np.sin(roll)) * dt],
            [-Thrust/self.quad.mass * (-np.sin(yaw)*np.sin(pitch)*np.sin(roll) - np.cos(yaw)*np.cos(roll)) * dt, -Thrust/self.quad.mass * (np.sin(yaw)*np.cos(pitch)*np.cos(roll) - np.cos(yaw)*np.sin(roll)) * dt, -Thrust/self.quad.mass * (np.cos(yaw)*np.sin(pitch)*np.cos(roll) + np.sin(yaw)*np.sin(roll)) * dt, -1/self.quad.mass * (np.sin(yaw)*np.sin(pitch)*np.cos(roll) - np.cos(yaw)*np.sin(roll)) * dt],
            [Thrust/self.quad.mass * (-np.cos(pitch)*np.sin(roll)) * dt, Thrust/self.quad.mass * (-np.sin(pitch)*np.cos(roll)) * dt, 0, 1/self.quad.mass * (np.cos(pitch)*np.cos(roll)) * dt]
        ))

        # update state prediction
        self.x = self._f(dt, mu, u)

        # update covariance
        self.P = F @ self.P @ F.T + G @ self.Q @ G.T

        # correction step based on predicted state and measurements, z is [z_x, z_y, z_z]
    def correct(self, z):
        # measurement matrix
        H = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

        # calculate Kalman gain
        K = self.P @ H.T @ np.linalg.pinv(H @ self.P @ H.T + self.R)

        # update state estimate
        self.x = self.x + K @ (z - H @ self.x)

        # update covariance
        self.P = (np.eye(3) - K @ H) @ self.P
