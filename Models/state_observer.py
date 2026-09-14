# Written by Jonah Habel 2026
# Flinders University
#
# state_observer.py
# -- defines the linearised state observer (linearised about hover) used for state feedback --

import numpy as np

g = 9.81 # m/s^2

class Observer:
    def __init__(self, quadcopter, sim):
        self.quad = quadcopter
        self.sim = sim
        self.x = np.array([
            [0.0], # x
            [0.0], # y
            [0.0], # z
            [0.0], # x velocity
            [0.0], # y velocity
            [0.0], # z velocity
            [0.0], # roll 
            [0.0], # pitch
            [0.0], # yaw
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

    # write states to quadcopter object
    def _write_back(self): 
        self.sim.position.x = float(self.x[0,0])
        self.sim.position.y = float(self.x[1,0])
        self.sim.position.z = max(float(self.x[2,0]), 0.0)

        self.sim.velocity.x = float(self.x[3,0])
        self.sim.velocity.y = float(self.x[4,0])
        self.sim.velocity.z = float(self.x[5,0])

        self.sim.attitude.roll = np.rad2deg(float(self.x[6,0]))
        self.sim.attitude.pitch = np.rad2deg(float(self.x[7,0]))
        self.sim.attitude.yaw = np.rad2deg(float(self.x[8,0]))

    def update(self, u, dt):

        # convert thrust as PWM to force (N)
        u[3,0] = float(u[3,0]) / self.quad.PWM_thrust_gain - self.quad.mass * g

        x_dot = self.A @ self.x + self.B @ u 

        self.x += x_dot * dt

        if self.x[2,0] <= 0.0:
            self.x[2,0] = 0.0
            self.x[5,0] = max(self.x[5,0], 0.0)

        self.quad.update_velocity(x = self.x[3,0], y = self.x[4,0], z = self.x[5,0])

        if self.quad.simulation_mode or self.quad.DT_mode and self.quad.viewer.ui.model_select.currentText().lower() == "linearised model":
            self._write_back()