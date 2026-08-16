# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot

from Classes.state_space_model import Nonlinear_Model
import numpy as np

class QuadSimulation:
    def __init__(self, quad):
        self.quad = quad
        self.model = Nonlinear_Model(quad)

        self.Kp_roll = 0.01
        self.Kp_pitch = 0.01
        self.Kp_yaw = 0.01

    def step(self, dt):

        p = self.model.x[9, 0]
        q = self.model.x[10, 0]
        r = self.model.x[11, 0]

        roll_rate_cmd  = self.quad.controls.roll
        pitch_rate_cmd = self.quad.controls.pitch
        yaw_rate_cmd   = self.quad.controls.yaw_rate

        tau_roll = self.Kp_roll * (roll_rate_cmd - p)
        tau_pitch = self.Kp_pitch * (pitch_rate_cmd - q)
        tau_yaw = self.Kp_yaw * (yaw_rate_cmd - r)

        u = np.array([
            [self.quad.controls.thrust],
            [tau_roll],
            [tau_pitch],
            [tau_yaw]
        ])

        self.model.update(u, dt)

        self.quad.position.x = float(self.model.x[0,0])
        self.quad.position.y = float(self.model.x[1,0])
        self.quad.position.z = float(self.model.x[2,0])

        self.quad.attitude.roll = float(self.model.x[6,0])
        self.quad.attitude.pitch = float(self.model.x[7,0])
        self.quad.attitude.yaw = float(self.model.x[8,0])