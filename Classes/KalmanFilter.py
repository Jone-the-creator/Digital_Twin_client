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
    def __init__(self):
        # control noise, ALTITUDE TUNED
        self.Q = np.array([
            [0.175, 0, 0],
            [0, 0.175, 0],
            [0, 0, 0.15]
        ])
        # measurement noise, ALTITUDE TUNED
        self.R = np.array([
            [0.05, 0, 0],
            [0, 0.05, 0],
            [0, 0, 0.025]
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
    
    # prediction step based on previous state and control, u for altitude is g * (T/Thover - 1)
    def predict(self, u, dt):
        # state transition matrix
        F = np.eye(3)

        # control matrix
        G = np.eye(3) * dt
        
        # update state prediction
        self.x = F @ self.x + G @ u

        # update covariance
        self.P = F @ self.P @ F.T + self.Q

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
