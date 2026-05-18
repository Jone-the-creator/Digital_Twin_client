import numpy as np

# only good for attitudes up to 45 degrees, numpy does algebra in radians
class Kalmanfilter():
    def __init__(self):
        # control noise
        self.Q = np.array([
            [0.175, 0, 0],
            [0, 0.175, 0],
            [0, 0, 0.025]
        ])
        # measurement noise
        self.R = np.array([
            [1.8, 0],
            [0, 1.8],
        ])
        # initial state
        self.x = np.zeros((3,1)) 

        # initialise covariance
        self.P = np.array([
            [0.05, 0, 0],
            [0, 0.05, 0],
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
