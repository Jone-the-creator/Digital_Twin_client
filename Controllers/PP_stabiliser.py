# Written by Jonah Habel 2026
# Flinders University
#
# PP_stabiliser.py
# -- defines the pole-placement stabiliser class stabilising the quadcopter with state-space control about hover --

import numpy as np
from scipy.signal import place_poles
from control import ctrb

g = 9.81 # m/s^2

class PPstabiliser():
    def __init__(self, state_observer):
        self.obs = state_observer

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
        self.yaw_setpoint = 0.0

        # integrated error terms
        self.integrated_z_error = 0 

        # adjustable altitude specifications
        self.settling_time_z = 1.25 # seconds
        self.overshoot_z = 10 # %
        self.delay_ratio_z = 0.0

        # adjustable attitude specifications
        self.settling_time_att = 4 # seconds
        self.overshoot_att = 20 # %



        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 5 # in degrees

        # -- MATRICES FOR ALTITUDE --
        self.A_z = np.array([
            [0,         1,             0],
            [0, -self.obs.quad.c[0,0], 0],
            [-1,        0,             0]
        ])

        self.B_z = np.array([
            [0],
            [1/self.obs.quad.mass],
            [0]
        ])

        self.K_z = self.altitude_spec_update()

        # -- MATRICES FOR ATTITUDE --
        self.A_att = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ])

        self.B_att = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])

        self.K_att = self.attitude_spec_update()
        print(self.K_att)

        print(np.linalg.matrix_rank(ctrb(self.A_att,self.B_att)))

    def hover():
        return None
        
    def altitude_control(self, altitude_setpoint, dt):
        altitude_error = self.obs.quad.position.z - altitude_setpoint
        self.integrated_z_error += altitude_error * dt
        self.integrated_z_error = np.clip(self.integrated_z_error, -0.1, 0.5)

        altitude_dot = self.obs.x[5,0] # observed altitude velocity
        hover_thrust = self.obs.quad.PWM_thrust_gain * self.obs.quad.mass * 9.81 
        x = np.array([
            [altitude_error],
            [altitude_dot],
            [-self.integrated_z_error]
        ])

        u = hover_thrust - (self.K_z @ x) * self.obs.quad.PWM_thrust_gain

        return u[0,0]

    def attitude_control(self):
        roll_error = self.obs.quad.attitude.roll - self.roll_setpoint

        pitch_error = self.obs.quad.attitude.pitch - self.pitch_setpoint

        yaw_error = self.obs.quad.attitude.yaw - self.yaw_setpoint

        x = np.array([
            [np.clip(roll_error, -self.max_angle, self.max_angle)],
            [np.clip(pitch_error, -self.max_angle, self.max_angle)],
            [np.clip(yaw_error, -self.max_angle, self.max_angle)],
        ])

        u = -self.K_att @ x
        print(u)
        return u

    def reset(self):
        # Reset setpoints
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0

        # Set current yaw to target
        self.yaw_rate_setpoint = 0.0

    def altitude_spec_update(self):
        # poles that adjust based on specifications
        self.zeta_z = np.sqrt(((np.log(self.overshoot_z/100))**2)/(np.pi**2+(np.log(self.overshoot_z/100))**2))
        self.omega_z = 4/(self.zeta_z*self.settling_time_z)
        self.delay_ratio_z = self.omega_z * self.obs.quad.dt # should be under 0.1 for stability
     
        # calculate poles based on adjustable specifications
        self.desired_poles_z = np.array([-self.zeta_z*self.omega_z * 5, 
                                -self.zeta_z*self.omega_z + (self.omega_z*np.sqrt(1-self.zeta_z**2))*1j, 
                                -self.zeta_z*self.omega_z - (self.omega_z*np.sqrt(1-self.zeta_z**2))*1j 
                                ])


        return place_poles(self.A_z,self.B_z,self.desired_poles_z).gain_matrix

    def attitude_spec_update(self):
        # poles that adjust based on specifications
        self.zeta_att = np.sqrt(((np.log(self.overshoot_att/100))**2)/(np.pi**2+(np.log(self.overshoot_att/100))**2))
        self.omega_att = 4/(self.zeta_att*self.settling_time_att)
     
        # calculate poles based on adjustable specifications
        self.desired_poles_att = np.array([
                                -self.zeta_att*self.omega_att + (self.omega_att*np.sqrt(1-self.zeta_att**2))*1j, 
                                -self.zeta_att*self.omega_att - (self.omega_att*np.sqrt(1-self.zeta_att**2))*1j,
                                -self.zeta_att*self.omega_att * 10                                
                                ])


        return place_poles(self.A_att,self.B_att,self.desired_poles_att).gain_matrix