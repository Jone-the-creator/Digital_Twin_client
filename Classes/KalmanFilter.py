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
            [0.0007, 0, 0],
            [0, 0.0007, 0],
            [0, 0, 0.025]
        ])
        # measurement noise
        self.R = np.array([
            [0.025, 0, 0, 0],
            [0, 0.025, 0, 0],
            [0, 0, 0.025, 0],
            [0, 0, 0, 0.1]
        ])
        # initial state
        self.x = np.array((
            [0.0], # roll
            [0.0], # pitch
            [0.0]  # yaw
        )) 

        # initialise covariance
        self.P = np.array([
            [0.0001, 0, 0],
            [0, 0.0001, 0],
            [0, 0, 0.06]
        ])

    def _f(self, dt, x, u):
        roll_rate = u[0,0]
        pitch_rate = u[1,0]
        yaw_rate = u[2,0]

        x[0,0] = x[0,0] + roll_rate * dt
        x[1,0] = x[1,0] + pitch_rate * dt
        x[2,0] = x[2,0] + yaw_rate * dt

        return x

 # prediction step based on previous state and control
    def predict(self, u, dt):
        mu = self.x.copy()
        # state transition matrix
        F = np.eye(3)

        # control matrix
        G = np.eye(3) * dt

        # update state prediction
        self.x = self._f(dt, mu, u)

        # update covariance
        self.P = F @ self.P @ F.T + G @ self.Q @ G.T

    def _h(self, x):
        z_hat = np.zeros((4,1))
        g = 9.81 # ms^-2

        z_hat[0,0] = g * np.sin(x[1,0])                    # a_x
        z_hat[1,0] = -g * np.sin(x[0,0]) * np.cos(x[1,0])  # a_y
        z_hat[2,0] = -g * np.cos(x[0,0]) * np.cos(x[1,0])  # a_z
        z_hat[3,0] = x[2,0]                                # yaw

        return z_hat


        # correction step based on predicted state and measurements, z is [a_y, a_x]
    def correct(self, z):
        g = 9.81 # ms^-2
        mu_hat = self.x
        P = self.P
        # measurement matrix
        H = np.array([
            [0, g * np.cos(mu_hat[1,0]), 0],
            [-g * np.cos(mu_hat[0,0]) * np.cos(mu_hat[1,0]), g * np.sin(mu_hat[0,0]) * np.sin(mu_hat[1,0]), 0],
            [g * np.sin(mu_hat[0,0]) * np.cos(mu_hat[1,0]), g * np.cos(mu_hat[0,0]) * np.sin(mu_hat[1,0]), 0],
            [0, 0, 1]
        ])

        z_hat = self._h(mu_hat)
        err = z - z_hat

        S = H @ P @ H.T + self.R

        # calculate Kalman gain
        K = self.P @ H.T @ np.linalg.pinv(S)

        # update state estimate
        self.x = mu_hat + K @ err

        # update covariance
        self.P = (np.eye(3) - K @ H) @ self.P

class pos_Kalmanfilter():
    def __init__(self, quadcopter):
        self.quad = quadcopter
        # control noise, ALTITUDE TUNED
        self.Q = np.array([
            [0.02, 0, 0, 0],
            [0, 0.02, 0, 0],
            [0, 0, 0.05, 0],
            [0, 0, 0, 1.0]
        ])
        # measurement noise, ALTITUDE TUNED
        self.R = np.array([
            [0.0022, 0, 0],
            [0, 0.053, 0],
            [0, 0, 0.00009]
        ])
        # initial state (1.5, 1.5, 0.0 for FFoF)
        self.x = np.array([
            [1.5],  # x
            [1.5],  # y
            [0.0],  # z
            [0.0],  # v_x
            [0.0],  # v_y
            [0.0],  # v_z
        ])

        self.prev_pos_x = self.x[0,0]
        self.prev_pos_y = self.x[1,0]

        # initialise covariance, ALTITUDE TUNED
        self.P = np.array([
            [0.045, 0, 0, 0, 0, 0],
            [0, 0.045, 0, 0, 0, 0],
            [0, 0, 0.001, 0, 0, 0],
            [0, 0, 0, 0.001, 0, 0],
            [0, 0, 0, 0, 0.001, 0],
            [0, 0, 0, 0, 0, 0.001]

        ])

    def _f(self, dt, x, u):
        Thrust = u[2,0] / self.quad.PWM_thrust_gain
        roll = u[0,0]
        pitch = u[1,0]
        x[0,0] = x[0,0]
        x[1,0] = x[1,0]
        x[2,0] = x[2,0] + x[5,0] * dt
        x[3,0] = 1/2 * x[3,0] + (x[0,0] - self.prev_pos_x) / (2 * dt) # change in x is current (corrected) and previous
        x[4,0] = 1/2 * x[4,0] + (x[1,0] - self.prev_pos_y) / (2 * dt) # change in y is current (corrected) and previous
        x[5,0] = Thrust/self.quad.mass * (np.cos(pitch)*np.cos(roll)) * dt

        # save the current position estimates before being corrected
        self.prev_pos_x = x[0,0]
        self.prev_pos_y = x[1,0]

        return x
    
    # prediction step based on previous state and control, u for altitude is g * (T/Thover - 1)
    def predict(self, u, dt):
        Thrust = u[2,0] / self.quad.PWM_thrust_gain
        roll = u[0,0]
        pitch = u[1,0]
        mu = self.x.copy()
        # state transition matrix
        F = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, dt],
            [1/(2*dt), 0, 0, 1/2, 0, 0],
            [0, 1/(2*dt), 0, 0, 1/2, 0],
            [0, 0, 0, 0, 0, 1]
        ])

        # control matrix
        G = np.array((
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [(-Thrust * np.cos(pitch)*np.sin(roll) * dt) /self.quad.mass, (-Thrust * np.sin(pitch)*np.cos(roll) * dt) /self.quad.mass, (np.cos(pitch)*np.cos(roll) * dt) /self.quad.mass]
        ))

        # update state prediction
        self.x = self._f(dt, mu, u)

        # update covariance
        self.P = F @ self.P @ F.T + G @ self.Q @ G.T

    def _h(self, x):
        z_hat = np.zeros((3,1))

        z_hat[0,0] = x[0,0]
        z_hat[1,0] = x[1,0]
        z_hat[2,0] = x[2,0]

        return z_hat

        # correction step based on predicted state and measurements, z is [x, y, z]
    def correct(self, z):
        mu = self.x
        P = self.P

        # measurement matrix
        H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0]
        ])

        z_hat = self._h(mu)
        err = z - z_hat

        S = H @ P @ H.T + self.R

        # calculate Kalman gain
        K = self.P @ H.T @ np.linalg.pinv(S)

        # update state estimate
        self.x = mu + K @ err

        # update covariance
        self.P = (np.eye(6) - K @ H) @ self.P
