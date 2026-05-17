import numpy as np

class Kalmanfilter():
    def __init__(self):
        self.Q = np.array([
            [0.05, 0, 0],
            [0, 0.05, 0],
            [0, 0, 0.1]
        ])
        self.R = np.array([
            [0.005, 0, 0],
            [0, 0.005, 0],
            [0, 0, 0]
        ])
        self.x = np.zeros((3,1)) 
        self.P = np.zeros((3,3))
    
    def predict(self, u, dt):
        F = np.eye(3)
        G = np.eye(3) * dt
        
        mu_hat = F @ self.x + G @ u

        P_hat = self.P.copy()
        P_hat = F @ P_hat @ F.T + self.Q

        self.x = mu_hat
        
        # self.x = np.clip(self.x, -np.pi, np.pi)
        self.P = P_hat
