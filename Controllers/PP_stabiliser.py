# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot

import numpy as np
import time
from scipy.signal import place_poles

class PPstabiliser():
    def __init__(self, state_observer):
        self.obs = state_observer

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
#        self.yaw_setpoint = 0.0

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 10 # in degrees

        # temporary calculation of pole-placement gains
        A = np.array([
            [0, 1],
            [0, -self.obs.quad.c[0,0]]
        ])

        B = np.array([
            [0],
            [1/self.obs.quad.mass]
        ])

        desired_poles = np.array([-3,-4])

        self.K = place_poles(A,B,desired_poles).gain_matrix
        print(self.K)
        
    def altitude_control(self, altitude_setpoint):
        altitude = self.obs.quad.position.z
        altitude_dot = self.obs.x[5,0] # observed altitude velocity
        hover_thrust = self.obs.quad.thrust_gain * self.obs.quad.mass * 9.81 

        thrust = hover_thrust - self.K[0,0] * altitude - self.K[0,1] * altitude_dot
    
        return thrust

    def reset(self):
        # Reset setpoints
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0

        # Set current yaw to target
        self.yaw_setpoint = self.quad.attitude.yaw