# Written by Jonah Habel 2026
# Flinders University

# -- Extended Kalman Filter used to estimate attitude and position capable of processing nonlinear terms --

import numpy as np

class SixDOFEKF():
    def __init__(self):
        # control noise
        self.Q = np.array([
            [0.25, 0, 0, 0, 0, 0],  # pitch
            [0, 0.25, 0, 0, 0, 0],  # roll
            [0, 0, 0.025, 0, 0, 0], # yaw
            [0, 0, 0, 0.175, 0, 0], # x
            [0, 0, 0, 0, 0.175, 0], # y
            [0, 0, 0, 0, 0, 0.175]  #z
        ])
        # measurement noise
        self.R = np.array([
            [0.025, 0, 0, 0, 0, 0],  # pitch
            [0, 0.025, 0, 0, 0, 0],  # roll
            [0, 0, 0.1, 0, 0, 0],    # yaw
            [0, 0, 0, 0.05, 0, 0]    # x
            [0, 0, 0, 0, 0.05, 0]    # y
            [0, 0, 0, 0, 0, 0.5]     # z
        ])

        # initial state vector x, [pitch, roll, yaw, x, y, z]
        self.x = np.array([
            [0.0], # pitch
            [0.0], # roll
            [0.0], # yaw
            [1.5], # x
            [1.5], # y
            [0.0]  # z
        ])

        self.x_vel = np.array([
            [0.0], # x velocity
            [0.0], # y velocity
            [0.0]  # z velocity
        ])

        # initialise covariance
        self.P = np.array([
            [0.0001, 0, 0, 0, 0, 0], # pitch
            [0, 0.0001, 0, 0, 0, 0], # roll
            [0, 0, 0.06, 0, 0, 0],   # yaw
            [0, 0, 0, 0.06, 0, 0],   # x
            [0, 0, 0, 0, 0.06, 0],   # y            
            [0, 0, 0, 0, 0, 0.06],   # z    
        ])

    # Provides the non-linear state transisition function f
    def _f(self, dt, x, u):
        # integrate controls as they are all velocities
        x[0,0] = u[0,0] * dt # update pitch
        x[1,0] = u[1,0] * dt # update roll
        x[2,0] = u[2,0] * dt # update yaw
        x[3,0] = self.x_vel[0,0] * dt # update x
        x[4,0] = self.x_vel[1,0] * dt # update y
        x[5,0] = self.x_vel[2,0] * dt # update alitude

        # update positional velocities based on control (thrust)
        self.x_vel[0,0] = -u[5,0]*(np.cos(x[2,0])*np.sin(x[0,0])*np.cos(x[1,0])+np.sin(x[2,0])*np.sin(x[1,0]))
        self.x_vel[0,0] = -u[5,0]*(np.sin(x[2,0])*np.sin(x[0,0])*np.cos(x[1,0])-np.cos(x[2,0])*np.sin(x[1,0]))
        self.x_vel[2,0] = u[5,0] * dt # input thrust (gravity removed) in m/s^2

        return x

    # prediction step based on previous state and control
    def predict(self, u, dt):
        prev_x = self.x.copy()

        # Jacobian F
        F = np.eye(3)

        # Jacobian G
        G = np.eye(3)

        # prediction step
        self.x = self._f(dt, prev_x, u)

        # wrap all attitudes
        self.x[0,0] = self.wrap(self.x[0,0])
        self.x[1,0] = self.wrap(self.x[1,0])
        self.x[2,0] = self.wrap(self.x[2,0])

        # update covariance
        self.P = F @ self.P @ np.transpose(F) + G @ self.Q @ np.transpose(G)

    def _h(self, x, vel):
        z_hat = np.atan2()



    def wrap(self, value):
    # Wrap function ensures that the value is wrapped such that it has value that lies between +/- pi.
    # This is used in calulating heanding to ensure and 2pi rotational ambuity is removed
        return (value + np.pi) % (2 * np.pi) - np.pi
