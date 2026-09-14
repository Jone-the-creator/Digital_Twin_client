# Written by Jonah Habel 2026
# Flinders University
#
# state_observer.py
# -- defines the linearised state observer (linearised about hover) used for state feedback --

import numpy as np
from scipy.signal import place_poles

g = 9.81 # m/s^2

class Observer:
    def __init__(self, quadcopter, sim):
        self.quad = quadcopter
        self.sim = None
        if sim is not None:
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

        self.observer_poles = np.array([
            -4.0,
            -4.5,
            -5.0,
            -5.5,
            -6.0,
            -6.5,
            -7.0,
            -7.5,
            -8.0
        ])

        Co = controllability_matrix(self.A, self.B)
        print("Controllability rank:", np.linalg.matrix_rank(Co), "/", self.A.shape[0])

        Ob = observability_matrix(self.A, self.C)
        print("Observability rank:", np.linalg.matrix_rank(Ob), "/", self.A.shape[0])

        self.L = place_poles(self.A.T, self.C.T, self.observer_poles).gain_matrix.T

    # write states to quadcopter object
    def _write_back(self): 
        if self.sim is None:
            return
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
        u = np.asarray(u, dtype=float).reshape(4,1).copy()
        y = np.array([
            [float(self.quad.position.x)],
            [float(self.quad.position.y)],
            [float(self.quad.position.z)],
            [np.deg2rad(float(self.quad.attitude.roll))],
            [np.deg2rad(float(self.quad.attitude.pitch))],
            [np.deg2rad(float(self.quad.attitude.yaw))],
        ], dtype=float)

        y_hat = self.C @ self.x
        y_err = y - y_hat
        y_err[5,0] = wrap(y_err[5,0])
            
        # convert thrust as PWM to force (N)
        u[3,0] = float(u[3,0]) / self.quad.PWM_thrust_gain - self.quad.mass * g

        x_dot = self.A @ self.x + self.B @ u + self.L @ y_err

        self.x += x_dot * dt

        if self.x[2,0] <= 0.0:
            self.x[2,0] = 0.0
            self.x[5,0] = max(self.x[5,0], 0.0)

        if self.sim is not None:
            self.sim.update_velocity(x = self.x[3,0], y = self.x[4,0], z = self.x[5,0])

        if (self.quad.simulation_mode or self.quad.DT_mode) and self.quad.viewer.ui.model_select.currentText().lower() == "linearised model":
            self._write_back()

def controllability_matrix(A, B):
    n = A.shape[0]

    return np.hstack([
        np.linalg.matrix_power(A, i) @ B
        for i in range(n)
    ])

def observability_matrix(A, C):
    n = A.shape[0]

    return np.vstack([
        C @ np.linalg.matrix_power(A, i)
        for i in range(n)
    ])

def wrap(angle):
    return (angle + np.pi) % (2*np.pi) - np.pi

    