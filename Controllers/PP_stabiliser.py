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

        print(self.A_aug.shape)
        print(self.B_aug.shape)

        C = ctrb(self.A_aug, self.B_aug)

        print("rank =", np.linalg.matrix_rank(C))
        print("states =", self.A_aug.shape[0])

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

        print(e_aug.T)
        u = -self.K @ e_aug

        roll_rate_cmd = -np.clip(np.rad2deg(u[0,0]), -self.max_angle_rate, self.max_angle_rate)
        pitch_rate_cmd = -np.clip(np.rad2deg(u[1,0]), -self.max_angle_rate, self.max_angle_rate)

        thrust_delta = float(u[3,0]) * self.obs.quad.PWM_thrust_gain
        thrust_cmd = self.obs.quad.hover_thrust - thrust_delta
        print(u)
        print(f"pitch_cmd = {pitch_rate_cmd:.2f}, roll_cmd = {roll_rate_cmd:.2f}, thrust_cmd = {thrust_cmd:.2f}")
        return roll_rate_cmd, pitch_rate_cmd, thrust_cmd
        
    def altitude_control(self, altitude_setpoint, dt):
        if self.obs.quad.simulation_mode and self.obs.quad.viewer.ui.model_select.currentText().lower() == "non-linear model":
            velocity_z = self.sim_non_linear.velocity.z
            altitude = self.sim_non_linear.position.z
        elif self.obs.quad.simulation_mode and self.obs.quad.viewer.ui.model_select.currentText().lower() == "linearised model":
            velocity_z = self.sim_non_linear.velocity.z
            altitude = self.sim_linear.position.z
        else:
            velocity_z = self.obs.x[5,0]
            altitude = self.obs.quad.position.z
        altitude_error = altitude_setpoint - altitude
        self.integrated_z_error += altitude_error * dt

        hover_thrust = self.obs.quad.PWM_thrust_gain * self.obs.quad.mass * 9.81 
        x = np.array([
            [altitude_error],
            [velocity_z],
            [self.integrated_z_error]
        ])

        u = hover_thrust - (self.K_z @ x) * self.obs.quad.PWM_thrust_gain

        return u[0,0]

    def attitude_control(self, dt):
        roll_error = np.deg2rad(self.roll_setpoint - self.obs.quad.attitude.roll)
        pitch_error = np.deg2rad(self.pitch_setpoint - self.obs.quad.attitude.pitch)

        x = np.array([
            [roll_error],
            [pitch_error],
            [np.clip(self.integrated_roll_error, -self.max_att_integration, self.max_att_integration)],
            [np.clip(self.integrated_pitch_error, -self.max_att_integration, self.max_att_integration)]
        ])

        u = -self.K_att @ x

        if abs(u[1,0]) < self.max_angle_rate:
            self.integrated_pitch_error += pitch_error * dt

        if abs(u[0,0]) < self.max_angle_rate:
            self.integrated_roll_error += roll_error * dt

        roll_cmd = np.clip(u[0,0], -self.max_angle_rate, self.max_angle_rate)
        pitch_cmd = np.clip(u[1,0], -self.max_angle_rate, self.max_angle_rate)
        print(f"from attitude controller: pitch_cmd = {pitch_cmd:.2f}, roll_cmd = {roll_cmd:.2f}")
        return -np.rad2deg(pitch_cmd), np.rad2deg(roll_cmd)

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
            -1+1j,
            -1-1j,
            -1.5+1.5j,
            -1.5-1.5j,
            -2+2j,
            -2-2j,
            -3,
            -1.2,
            -0.8,
            -0.5,
        ])


        return place_poles(self.A_aug,self.B_aug,desired_poles).gain_matrix

    def attitude_spec_update(self):
        # poles that adjust based on specifications
        self.zeta_att = np.sqrt(((np.log(self.overshoot_att/100))**2)/(np.pi**2+(np.log(self.overshoot_att/100))**2))
        self.omega_att = 4/(self.zeta_att*self.settling_time_att)
     
        # calculate poles based on adjustable specifications
        self.desired_poles_att = np.array([
                                -self.zeta_att*self.omega_att + (self.omega_att*np.sqrt(1-self.zeta_att**2))*1j, 
                                -self.zeta_att*self.omega_att - (self.omega_att*np.sqrt(1-self.zeta_att**2))*1j,
                                -self.zeta_att*self.omega_att * 1.1,
                                -self.zeta_att*self.omega_att * 1.15,                             
                                ])

        return place_poles(self.A_att,self.B_att,self.desired_poles_att).gain_matrix