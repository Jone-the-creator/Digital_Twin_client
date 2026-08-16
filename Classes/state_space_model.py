# Written by Jonah Habel 2026
# Flinders University

import numpy as np
import state_space as ss

g = 9.81 # m/s^2

class Nonlinear_Model:
    def __init__(self, quadcopter):
        self.quad = quadcopter
        self.x = np.array([
            [self.quad.position.x],
            [self.quad.position.y],
            [max(self.quad.position.z, 0.0)],
            [self.quad.velocity.x],
            [self.quad.velocity.y],
            [self.quad.velocity.z],
            [self.quad.attitude.roll],
            [self.quad.attitude.pitch],
            [self.quad.attitude.yaw],
        ])

        self.A = np.array([
            [0, 0, 0, 1, 0, 0, 0,  0, 0],
            [0, 0, 0, 0, 1, 0, 0,  0, 0],
            [0, 0, 0, 0, 0, 1, 0,  0, 0],
            [0, 0, 0, -self.quad.kd / self.quad.mass, 0, 0, 0, -g, 0],
            [0, 0, 0, 0, -self.quad.kd / self.quad.mass, 0, g,  0, 0],
            [0, 0, 0, 0, 0, -self.quad.kd / self.quad.mass, 0,  0, 0],
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

    # write states to quadcopter object
    def _write_back(self): 
        self.quad.position.x = float(self.x[0,0])
        self.quad.position.y = float(self.x[1,0])
        self.quad.position.z = max(float(self.x[2,0]), 0.0)

        self.quad.velocity.x = float(self.x[3,0])
        self.quad.velocity.y = float(self.x[4,0])
        self.quad.velocity.z = float(self.x[5,0])

        self.quad.attitude.roll = np.rad2deg(float(self.x[6,0]))
        self.quad.attitude.pitch = np.rad2deg(float(self.x[7,0]))
        self.quad.attitude.yaw = np.rad2deg(float(self.x[8,0]))

    def update(self, u, dt):
        # update state matrix
        self.x = np.array([
            [self.quad.position.x],
            [self.quad.position.y],
            [max(self.quad.position.z, 0.0)],
            [self.quad.velocity.x],
            [self.quad.velocity.y],
            [self.quad.velocity.z],
            [np.deg2rad(self.quad.attitude.roll)],
            [np.deg2rad(self.quad.attitude.pitch)],
            [np.deg2rad(self.quad.attitude.yaw)]
        ])

        # convert thrust as PWM to force (N)
        # divides by gravity (in PWM) and removes gravitational force
        u[3,0] = (float(u[3,0]) / self.quad.PWM_thrust_gain * self.quad.mass * g) - 1.0 

        x_dot = self.A @ self.x + self.B @ u 

        x_dot[5,0] -= (0.1 * x_dot[2,0]) # linear aerodynamic damping
        x_dot[5,0] -= (0.5 * x_dot[2,0] * np.abs(x_dot[2,0])) # non-linear aerodynamic damping


        self.x += x_dot * dt

        if self.x[2,0] <= 0.0:
            self.x[2,0] = 0.0
            self.x[5,0] = max(self.x[5,0], 0.0)

        self._write_back()