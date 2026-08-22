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
        self.integrated_roll_error = 0
        self.integrated_pitch_error = 0

        # adjustable altitude specifications
        self.settling_time_z = 1.25 # seconds
        self.overshoot_z = 10 # %
        self.delay_ratio_z = 0.0

        # adjustable attitude specifications
        self.settling_time_att = 4 # seconds
        self.overshoot_att = 20 # %

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 5 # in degrees

        # pole arrays
        self.desired_poles_z = np.zeros((1,3))
        self.desired_poles_att = np.zeros((1,5))

        # -- CONTROL MATRICES --
        # 12 x 12 A matrix (x dot based on x)
        self.A = np.array([
            [0,         1,             0, 0, 0, 0, 0, 0],
            [0, -self.obs.quad.c[0,0], 0, 0, 0, 0, 0, 0],
            [0,         0,             0, 0, 0, 0, 0, 0],
            [0,         0,             0, 0, 0, 0, 0, 0],
            [0,         0,             0, 0, 0, 0, 0, 0],
            [-1,        0,             0, 0, 0, 0, 0, 0],
            [0,         0,             -1, 0, 0, 0, 0, 0],
            [0,         0,             0, -1, 0, 0, 0, 0],
        ])

        self.B = np.array([
            [0, 0, 0,           0],
            [0, 0, 0, 1/self.obs.quad.mass],
            [1, 0, 0,           0],
            [0, 1, 0,           0],
            [0, 0, 1,           0],
            [0, 0, 0,           0],
            [0, 0, 0,           0],
            [0, 0, 0,           0],
        ])

        # initial update of desired poles
        self.altitude_spec_update()
        self.attitude_spec_update()
        
        print(self.desired_poles_z)
        print(self.desired_poles_att)

        self.desired_poles = np.hstack((
            self.desired_poles_z, # altitude state poles
            self.desired_poles_att, # attitude state poles
        )).flatten()

        self.K = place_poles(self.A,self.B,self.desired_poles).gain_matrix
        print(self.K)

    def hover(self, altitude_setpoint, dt):
        u = np.zeros((3,1)) # used for control output
        hover_thrust = self.obs.quad.PWM_thrust_gain * self.obs.quad.mass * 9.81 

        # calculate real setpoint errors
        altitude_error = altitude_setpoint - self.obs.quad.position.z
        roll_error = np.deg2rad(self.roll_setpoint - self.obs.quad.attitude.roll)
        pitch_error = np.deg2rad(self.pitch_setpoint - self.obs.quad.attitude.pitch)

        # integrate errors
        self.integrated_z_error += altitude_error * dt
        self.integrated_roll_error -= roll_error * dt
        self.integrated_pitch_error -= pitch_error * dt

        # clip integrators
        self.integrated_z_error = np.clip(self.integrated_z_error, -0.1, 0.1)
        self.integrated_roll_error = np.clip(self.integrated_roll_error, -0.25, 0.25)
        self.integrated_pitch_error = np.clip(self.integrated_pitch_error, -0.25, 0.25)

        x = np.array([
            [altitude_error],     # z
            [self.obs.x[5,0]],              # z velocity
            [roll_error],  # roll
            [pitch_error], # pitch
            [np.deg2rad(self.obs.quad.attitude.yaw)],   # yaw
            [self.integrated_z_error],      # integrated altitude error 
            [self.integrated_roll_error],   # integrated roll error
            [self.integrated_pitch_error]   # integrated pitch error
        ])

        u = -self.K @ x
        print(f"(pre_transform) roll dot = {u[0,0]}, pitch dot = {u[1,0]}, yaw dot = {u[2,0]}, thrust = {u[3,0]}")
        u[0,0] = u[0,0]
        u[1,0] = u[1,0]
        u[2,0] = u[2,0]
        # u[3,0] *= self.obs.quad.PWM_thrust_gain
        u[3,0] = hover_thrust - u[3,0] * self.obs.quad.PWM_thrust_gain
        print(f"roll dot = {u[0,0]}, pitch dot = {u[1,0]}, yaw dot = {u[2,0]}, thrust = {u[3,0]}")
        return u
        
    # def altitude_control(self, altitude_setpoint, dt):
    #     altitude_error = self.obs.quad.position.z - altitude_setpoint
    #     self.integrated_z_error += altitude_error * dt
    #     self.integrated_z_error = np.clip(self.integrated_z_error, -0.1, 0.1)

    #     altitude_dot = self.obs.x[5,0] # observed altitude velocity
    #     hover_thrust = self.obs.quad.PWM_thrust_gain * self.obs.quad.mass * 9.81 
    #     x = np.array([
    #         [altitude_error],
    #         [altitude_dot],
    #         [-self.integrated_z_error]
    #     ])

    #     u = hover_thrust - (self.K_z @ x) * self.obs.quad.PWM_thrust_gain

    #     return u[0,0]

    # def attitude_control(self):
    #     roll_error = self.obs.quad.attitude.roll - self.roll_setpoint

    #     pitch_error = self.obs.quad.attitude.pitch - self.pitch_setpoint

    #     yaw_error = self.obs.quad.attitude.yaw - self.yaw_setpoint

    #     x = np.array([
    #         [np.clip(roll_error, -self.max_angle, self.max_angle)],
    #         [np.clip(pitch_error, -self.max_angle, self.max_angle)],
    #         [np.clip(yaw_error, -self.max_angle, self.max_angle)],
    #     ])

    #     u = -self.K_att @ x
    #     print(u)
    #     return u

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
        self.desired_poles_z = np.array([
                                -self.zeta_z*self.omega_z + (self.omega_z*np.sqrt(1-self.zeta_z**2))*1j, 
                                -self.zeta_z*self.omega_z - (self.omega_z*np.sqrt(1-self.zeta_z**2))*1j,
                                -self.zeta_z*self.omega_z * 5  
                                ])
        

    def attitude_spec_update(self):
        # poles that adjust based on specifications
        self.zeta_att = np.sqrt(((np.log(self.overshoot_att/100))**2)/(np.pi**2+(np.log(self.overshoot_att/100))**2))
        self.omega_att = 4/(self.zeta_att*self.settling_time_att)
     
        # calculate poles based on adjustable specifications
        self.desired_poles_att = np.array([
                                -self.zeta_att*self.omega_att + (self.omega_att*np.sqrt(1-self.zeta_att**2))*1j, 
                                -self.zeta_att*self.omega_att - (self.omega_att*np.sqrt(1-self.zeta_att**2))*1j, 
                                -self.zeta_att*self.omega_att * 5,
                                -self.zeta_att*self.omega_att * 6,
                                -self.zeta_att*self.omega_att * 7                                    
                                ])