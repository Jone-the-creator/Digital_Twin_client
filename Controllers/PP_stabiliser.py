# Written by Jonah Habel 2026
# Flinders University
#
# PP_stabiliser.py
# -- defines the pole-placement stabiliser class stabilising the quadcopter with state-space control about hover --

import numpy as np
from scipy.signal import place_poles
from control import ctrb
import control as co

g = 9.81 # m/s^2

class PPstabiliser():
    def __init__(self, state_observer, sim_non_linear, sim_linear):
        self.obs = state_observer
        self.sim_non_linear = sim_non_linear
        self.sim_linear = sim_linear

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
        self.yaw_setpoint = 0.0

        # integrated error terms
        self.integrated_z_error = 0 
        self.integrated_roll_error = 0 
        self.integrated_pitch_error = 0 
        self.max_att_integration = 2

        # adjustable altitude specifications
        self.settling_time_z = 4 # seconds
        self.overshoot_z = 10 # %
        self.delay_ratio_z = 0.0

        # adjustable attitude specifications
        self.settling_time_att = 0.75 # seconds
        self.overshoot_att = 3.5 # %
        self.zeta_att = np.sqrt(((np.log(self.overshoot_att/100))**2)/(np.pi**2+(np.log(self.overshoot_att/100))**2))
        self.omega_att = 4/(self.zeta_att*self.settling_time_att)

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle_rate = 15 # in degrees/s

        self.A_aug = np.block([
            [self.obs.A, np.zeros((9,1))],
            [-np.array([[0, 0, 1, 0, 0, 0, 0, 0, 0]]), np.zeros((1,1))],
        ])

        self.B_aug = np.vstack([
            self.obs.B,
            np.zeros((1,4))
        ])

        # print(self.A_aug.shape)
        # print(self.B_aug.shape)

        C = ctrb(self.A_aug, self.B_aug)

        # print("rank =", np.linalg.matrix_rank(C))
        # print("states =", self.A_aug.shape[0])

        self.K = self.altitude_spec_update()

    def hover(self, altitude_setpoint, dt):
        # x setpoint states, any that aren't to be used are set to zero by using the observed value
        x_sp = np.array([
            [self.obs.x[0,0]],
            [self.obs.x[1,0]],
            [altitude_setpoint],
            [self.obs.x[3,0]],
            [self.obs.x[4,0]],
            [0],
            [np.deg2rad(self.roll_setpoint)],
            [np.deg2rad(self.pitch_setpoint)],
            [self.obs.x[8,0]]
        ])

        error = x_sp - self.obs.x 

        self.integrated_z_error += error[2,0] * dt

        # augmented error matrix with integratal states
        e_aug = np.vstack(
            [error,
            -self.integrated_z_error]
        )

        # print(e_aug.T)
        u = -self.K @ e_aug

        roll_rate_cmd = -np.clip(np.rad2deg(u[0,0]), -self.max_angle_rate, self.max_angle_rate)
        pitch_rate_cmd = -np.clip(np.rad2deg(u[1,0]), -self.max_angle_rate, self.max_angle_rate)

        thrust_delta = float(u[3,0]) * self.obs.quad.PWM_thrust_gain
        thrust_cmd = self.obs.quad.hover_thrust - thrust_delta
        
        return roll_rate_cmd, pitch_rate_cmd, thrust_cmd

    def reset(self):
        # Reset setpoints
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0

        # Reset integral errors
        self.integrated_z_error = 0.0
        self.integrated_pitch_error = 0.0
        self.integrated_roll_error = 0.0

        # Set current yaw to target
        self.yaw_rate_setpoint = 0.0

    def altitude_spec_update(self):
        # poles that adjust based on specifications
        self.zeta_z = np.sqrt(((np.log(self.overshoot_z/100))**2)/(np.pi**2+(np.log(self.overshoot_z/100))**2))
        self.omega_z = 4/(self.zeta_z*self.settling_time_z)
        self.delay_ratio_z = self.omega_z * self.obs.quad.dt # should be under 0.1 for stability

        desired_poles = np.array([
            -1+1.37j, -1-1.37j,
            -1.05+1.37j, -1.05-1.37j,
            -1.15+1.37j, -1.15-1.37j,
            -1.8,
            -1.9,
            -2.0,
            -0.2
        ])


        return place_poles(self.A_aug,self.B_aug,desired_poles).gain_matrix
