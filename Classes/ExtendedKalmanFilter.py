# Written by Jonah Habel 2026
# Flinders University

# -- Extended Kalman Filter used to estimate attitude and position capable of processing nonlinear terms --

import numpy as np

class NineDOF_EKF():
    def __init__(self):
        # control noise
        self.Q = np.array([
            [0.25, 0, 0, 0],  # pitch
            [0, 0.25, 0, 0],  # roll
            [0, 0, 0.025, 0], # yaw
            [0, 0, 0, 0.1]   # thrust
        ])
        # measurement noise
        self.R = np.array([
            [0.025, 0, 0, 0, 0, 0, 0, 0, 0],  # pitch
            [0, 0.025, 0, 0, 0, 0, 0, 0, 0],  # roll
            [0, 0, 0.1, 0, 0, 0, 0, 0, 0],    # yaw
            [0, 0, 0, 0.05, 0, 0, 0, 0, 0],   # x
            [0, 0, 0, 0, 0.05, 0, 0, 0, 0],   # y
            [0, 0, 0, 0, 0, 0.5, 0, 0, 0],    # z
            [0, 0, 0, 0, 0, 0, 0, 0, 0],      # x velocity
            [0, 0, 0, 0, 0, 0, 0, 0, 0],      # y velocity
            [0, 0, 0, 0, 0, 0, 0, 0, 0],      # z velocity
        ])

        # initial state vector x, [pitch, roll, yaw, x, y, z]
        self.x = np.array([
            [0.0], # pitch
            [0.0], # roll
            [0.0], # yaw
            [1.5], # x
            [1.5], # y
            [0.0], # z
            [0.0], # x velocity
            [0.0], # y velocity
            [0.0]  # z velocity
        ])

        # initialise covariance
        self.P = np.array([
            [0.0001, 0, 0, 0, 0, 0, 0, 0, 0], # pitch
            [0, 0.0001, 0, 0, 0, 0, 0, 0, 0], # roll
            [0, 0, 0.06, 0, 0, 0, 0, 0, 0],   # yaw
            [0, 0, 0, 0.06, 0, 0, 0, 0, 0],   # x
            [0, 0, 0, 0, 0.06, 0, 0, 0, 0],   # y            
            [0, 0, 0, 0, 0, 0.06, 0, 0, 0],   # z
            [0, 0, 0, 0, 0, 0, 0.01, 0, 0],   # x velocity
            [0, 0, 0, 0, 0, 0, 0, 0.01, 0],   # y velocity
            [0, 0, 0, 0, 0, 0, 0, 0, 0.01],   # z velocity 
        ])

    # Provides the non-linear state transisition function f
    def _f(self, dt, x, u):
        # integrate controls as they are all velocities
        x[0,0] += u[0,0] * dt # update pitch
        x[1,0] += u[1,0] * dt # update roll
        x[2,0] += u[2,0] * dt # update yaw
        x[3,0] += x[6,0] * dt # update x
        x[4,0] += x[7,0] * dt # update y
        x[5,0] += x[8,0] * dt # update z
        x[6,0] += -u[3,0]*(np.cos(x[2,0])*np.sin(x[0,0])*np.cos(x[1,0])+np.sin(x[2,0])*np.sin(x[1,0])) * dt # update x velocity
        x[7,0] += -u[3,0]*(np.sin(x[2,0])*np.sin(x[0,0])*np.cos(x[1,0])-np.cos(x[2,0])*np.sin(x[1,0])) * dt # update y velocity
        x[8,0] += u[3,0] * dt  # update z velocity

        return x

    # prediction step based on previous state and control
    def predict(self, u, dt):
        prev_x = self.x.copy()

        # define state Jacobian F
        F = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0, 0],  
            [0, 1, 0, 0, 0, 0, 0, 0, 0],  
            [0, 0, 1, 0, 0, 0, 0, 0, 0],  
            [0, 0, 0, 1, 0, 0, dt, 0, 0],  
            [0, 0, 0, 0, 1, 0, 0, dt, 0],  
            [0, 0, 0, 0, 0, 1, 0, 0, dt],    
            [-u[3,0]*dt*(np.cos(prev_x[2,0])*np.cos(prev_x[0,0])*np.cos(prev_x[1,0])+np.sin(prev_x[2,0])*np.sin(prev_x[1,0])),
            -u[3,0]*dt*(-np.cos(prev_x[2,0])*np.sin(prev_x[0,0])*np.sin(prev_x[1,0])+np.sin(prev_x[2,0])*np.cos(prev_x[1,0])),
            -u[3,0]*dt*(np.sin(prev_x[2,0])*np.sin(prev_x[0,0])*np.cos(prev_x[1,0])-np.cos(prev_x[2,0])*np.sin(prev_x[1,0])), 0, 0, 0, 1, 0, 0],  
            [-u[3,0]*dt*(-np.sin(prev_x[2,0])*np.cos(prev_x[0,0])*np.cos(prev_x[1,0])-np.cos(prev_x[2,0])*np.sin(prev_x[1,0])),
            -u[3,0]*dt*(np.sin(prev_x[2,0])*np.sin(prev_x[0,0])*np.sin(prev_x[1,0])-np.cos(prev_x[2,0])*np.cos(prev_x[1,0])), 
            -u[3,0]*dt*(-np.cos(prev_x[2,0])*np.sin(prev_x[0,0])*np.cos(prev_x[1,0])-np.sin(prev_x[2,0])*np.sin(prev_x[1,0])), 0, 0, 0, 0, 1, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 1], 
        ])

        # define control Jacobian G
        G = np.array([
            [dt, 0, 0, 0],
            [0, dt, 0, 0], 
            [0, 0, dt, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, -dt*(np.cos(prev_x[2,0])*np.sin(prev_x[0,0])*np.cos(prev_x[1,0])+np.sin(prev_x[2,0])*np.sin(prev_x[1,0]))],
            [0, 0, 0, -dt*(np.sin(prev_x[2,0])*np.sin(prev_x[0,0])*np.cos(prev_x[1,0])-np.cos(prev_x[2,0])*np.sin(prev_x[1,0]))],
            [0, 0, 0, dt]
        ])

        # prediction step
        self.x = self._f(dt, prev_x, u)

        # wrap all attitudes
        self.x[0,0] = self.wrap(self.x[0,0])
        self.x[1,0] = self.wrap(self.x[1,0])
        self.x[2,0] = self.wrap(self.x[2,0])

        # update covariance
        self.P = F @ self.P @ np.transpose(F) + G @ self.Q @ np.transpose(G)

    def _h(self, x):
        z_hat = x
        z_hat[2,0] = np.atan2(x[6,0],x[7,0])

        return z_hat


    def correct(self, z):
        mu = self.x
        P = self.P

        # define measurement Jacobian H (TO BE UPDATED)
        H = np.eye(9)

        z_hat = self._h(mu)
        err = z - z_hat

        # wrap all angles
        err[0,0] = self.wrap(err[0,0])
        err[1,0] = self.wrap(err[1,0])
        err[2,0] = self.wrap(err[2,0])

        S = H @ P @ H.T + self.R
        K = P @ H.T @ np.linalg.pinv(S)

        self.x = mu + K @ err
        self.P = (np.eye(9)- K @ H) @ P

        # wrap all attitudes
        self.x[0,0] = self.wrap(self.x[0,0])
        self.x[1,0] = self.wrap(self.x[1,0])
        self.x[2,0] = self.wrap(self.x[2,0])

    def wrap(self, value):
    # Wrap function ensures that the value is wrapped such that it has value that lies between +/- pi.
    # This is used in calulating heanding to ensure and 2pi rotational ambuity is removed
        return (value + np.pi) % (2 * np.pi) - np.pi
