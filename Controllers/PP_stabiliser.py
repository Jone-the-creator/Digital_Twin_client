# Written by Jonah Habel 2026
# Flinders University
#
# PP_stabiliser.py
# -- defines the pole-placement stabiliser class stabilising the quadcopter with state-space control about hover --

import numpy as np
from scipy.signal import place_poles

class PPstabiliser():
    def __init__(self, state_observer):
        self.obs = state_observer

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
        self.yaw_rate_setpoint = 0.0

        # integrated error terms
        self.integrated_z_error = 0 
        self.integrated_yaw_error = 0

        # adjustable specifications
        self.settling_time_z = 1.25 # seconds
        self.overshoot_z = 10 # %


        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 10 # in degrees

        # temporary calculation of pole-placement gains
        self.A = np.array([
            [0,         1,             0],
            [0, -self.obs.quad.c[0,0], 0],
            [-1,        0,             0]
        ])

        self.B = np.array([
            [0],
            [1/self.obs.quad.mass],
            [0]
        ])

        # poles that adjust based on specifications
        self.zeta_z = np.sqrt(((np.log(self.overshoot_z/100))**2)/(np.pi**2+(np.log(self.overshoot_z/100))**2))
        self.omega_z = 4/(self.zeta_z*self.settling_time_z)
     
        # calculate poles based on adjustable specifications
        self.desired_poles = np.array([-self.zeta_z*self.omega_z * 100, 
                                -self.zeta_z*self.omega_z + (self.omega_z*np.sqrt(1-self.zeta_z**2))*1j, 
                                -self.zeta_z*self.omega_z - (self.omega_z*np.sqrt(1-self.zeta_z**2))*1j 
                                ])


        self.K_z = place_poles(self.A,self.B,self.desired_poles).gain_matrix
        print(self.K_z)

    def hover():
        return None
        
    def altitude_control(self, altitude_setpoint, dt):
        altitude_error = self.obs.quad.position.z - altitude_setpoint
        self.integrated_z_error += altitude_error * dt

        altitude_dot = self.obs.x[5,0] # observed altitude velocity
        hover_thrust = self.obs.quad.PWM_thrust_gain * self.obs.quad.mass * 9.81 
        x = np.array([
            [altitude_error],
            [altitude_dot],
            [-self.integrated_z_error]
        ])

        u = hover_thrust - (self.K_z @ x) * self.obs.quad.PWM_thrust_gain

        return u[0,0]

    def attitude_control():
        return None

    # def _pitch_control(self, pitch_setpoint, dt):
    #     x = 


    # def _yaw_control(self, yaw_setpoint, dt):
    #     x = np.array([
    #         []
    #     ])

        u = 0.0

        return u

    def reset(self):
        # Reset setpoints
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0

        # Set current yaw to target
        self.yaw_rate_setpoint = 0.0