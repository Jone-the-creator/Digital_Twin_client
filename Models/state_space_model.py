# Written by Jonah Habel 2026
# Flinders University
#
# state_space_model.py
# -- defines the variable non-linear model of the quadcopter, to be used for simulation representation --

import numpy as np
import state_space as ss

g = 9.81 # m/s^2

class Nonlinear_Model:
    def __init__(self, quadcopter, sim):
        self.quad = quadcopter
        self.sim = sim
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
        # update state matrix
        self.x = np.array([
            [self.sim.position.x],
            [self.sim.position.y],
            [max(self.sim.position.z, 0.0)],
            [self.sim.velocity.x],
            [self.sim.velocity.y],
            [self.sim.velocity.z],
            [np.deg2rad(self.sim.attitude.roll)],
            [np.deg2rad(self.sim.attitude.pitch)],
            [np.deg2rad(self.sim.attitude.yaw)]
        ])

        # convert thrust as PWM to force (N)
        u[3,0] = float(u[3,0]) / self.quad.PWM_thrust_gain

        x_dot = np.array([
            [self.x[3,0]],
            [self.x[4,0]],
            [self.x[5,0]],
            [-((u[3,0]/self.quad.mass)\
            *(np.cos(self.x[8,0])*np.sin(self.x[7,0])*np.cos(self.x[6,0]) + np.sin(self.x[8,0])*np.sin(self.x[6,0])))], # rotate positional movements from body to navigational frame
            [-((u[3,0]/self.quad.mass)\
            *(np.sin(self.x[8,0])*np.sin(self.x[7,0])*np.cos(self.x[6,0]) - np.cos(self.x[8,0])*np.sin(self.x[6,0])))], # rotate positional movements from body to navigational frame
            [(u[3,0]/self.quad.mass)*(np.cos(self.x[6,0])*np.cos(self.x[7,0])) - g # rotate thrust to earth frame z axis, and subtract gravity
            - (self.quad.c[0,0] * self.x[5,0]) - (self.quad.c[1,0] * self.x[5,0] * np.abs(self.x[5,0]))], # altitude linear and non-linear aerodynamic damping
            [u[0,0]],
            [u[1,0]],
            [u[2,0]]
        ])

        self.x += x_dot * dt

        if self.x[2,0] <= 0.0:
            self.x[2,0] = 0.0
            self.x[5,0] = max(self.x[5,0], 0.0)

        if self.quad.simulation_mode and self.quad.viewer.ui.model_select.currentText().lower() == "non-linear model":
            self._write_back()

        if abs(self.x[2,0]) > 0.5:
            print(
            f"z={self.x[2,0]:.2f}, "
            f"vz={self.x[5,0]:.2f}, "
            f"thrust={u[3,0]:.2f}"
            )