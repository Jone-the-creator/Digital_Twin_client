# Written by Jonah Habel 2026
# Flinders University

import numpy as np

g = 9.81 # m/s^2

class Observer:
    def __init__(self, quadcopter):
        self.quad = quadcopter
        self.x = np.array([
            [0.0],
            [0.0],
            [0.0],
            [0.0],
            [0.0],
            [0.0],
            [0.0],
            [0.0],
            [0.0],
        ])

        self.A = np.array([
            [0, 0, 0, 1, 0, 0, 0,  0, 0],
            [0, 0, 0, 0, 1, 0, 0,  0, 0],
            [0, 0, 0, 0, 0, 1, 0,  0, 0],
            [0, 0, 0, 0, 0, 0, 0,  -g, 0],
            [0, 0, 0, 0, 0, 0, g,  0, 0],
            [0, 0, 0, 0, 0, -self.quad.c[0,0], 0,  0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0],
        ])

        self.B = np.array([
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 1/self.quad.mass],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
        ])

        self.C = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1]
        ])

        self.D = np.array([
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])

    def update(self, u, dt):

        # convert thrust as PWM to force (N)
        u[3,0] = float(u[3,0]) / self.quad.PWM_thrust_gain - self.quad.mass * g

        x_dot = self.A @ self.x + self.B @ u 

        self.x += x_dot * dt

        if self.x[2,0] <= 0.0:
            self.x[2,0] = 0.0
            self.x[5,0] = max(self.x[5,0], 0.0)