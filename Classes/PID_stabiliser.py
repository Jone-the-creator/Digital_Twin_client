# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot

import numpy as np
import time

class PIDstabiliser():
    def __init__(self, quadcopter):
        self.quad = quadcopter
        

        self.z_trim = 0.0

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
#        self.yaw_setpoint = 0.0

        # Altitude error variables
        self.altitude_integral = 0.0
        self.prev_altitude_error = 0.0
        self.altitude_derivative = 0.0

        # Pitch error variaQbles
        self.pitch_integral = 0.0
        self.prev_pitch_error = 0.0
        self.pitch_derivative = 0.0

        # Roll error variaQbles
        self.roll_integral = 0.0
        self.prev_roll_error = 0.0
        self.roll_derivative = 0.0

        # initialise current attitude readings
        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch
        self.pitch_trim = self.pitch
        self.roll_trim = self.roll

        self._pitch_sum = 0.0
        self._roll_sum = 0.0

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 10 # in degrees

        # max integral term (limit integral windup)
        self.max_int = 40

        self.DC_gain_z = 13000.0
        self.Kp_z = 3.5
        self.Ki_z = 0.75
        self.Kd_z = 0.65

        self.Kp_att = 2.0
        self.Ki_att = 0.0
        self.Kd_att = 0.5



    # hover mode, will control attitude with 0 setpoints
    def hover(self, altitude_setpoint):
        # --- ALTITUDE CONTROL ---
        altitude = self.quad.position.z
        hover_thrust = self.DC_gain_z * self.quad.mass * 9.81 

        altitude_error = altitude_setpoint - altitude
        self.altitude_integral += altitude_error * self.quad.dt
        self.altitude_integral = np.clip(self.altitude_integral, -self.max_int, self.max_int)
        self.altitude_derivative = (altitude_error - self.prev_altitude_error) / self.quad.dt
        self.prev_altitude_error = altitude_error

        thrust = altitude_error * self.Kp_z * self.DC_gain_z + self.altitude_integral * self.Ki_z * self.DC_gain_z + self.altitude_derivative * self.Kd_z * self.DC_gain_z + hover_thrust

        # # --- ATTITUDE CONTROL ---

        # Calculate attitude errors
        pitch_error = -np.clip(self.pitch_setpoint - (self.quad.attitude.pitch ), -self.max_angle, self.max_angle)
        roll_error = np.clip(self.roll_setpoint - (self.quad.attitude.roll), -self.max_angle, self.max_angle)

        self.pitch_integral += pitch_error * self.quad.dt
        self.roll_integral += roll_error * self.quad.dt
        self.pitch_integral = np.clip(self.pitch_integral, -self.max_int, self.max_int)
        self.roll_integral = np.clip(self.roll_integral, -self.max_int, self.max_int)

        self.pitch_derivative = pitch_error - self.prev_pitch_error 
        self.roll_derivative = roll_error - self.prev_roll_error
        self.prev_pitch_error = pitch_error
        self.prev_roll_error = roll_error

        # Pitch and roll rate commands calculated with PID based on error in x and y (assuming constant yaw)
        pitch_rate = pitch_error * self.Kp_att + self.pitch_integral * self.Ki_att + self.pitch_derivative * self.Kd_att
        roll_rate = roll_error * self.Kp_att + self.roll_integral * self.Ki_att + self.roll_derivative * self.Kd_att

        return pitch_rate, roll_rate, thrust
        
    def altitude_control(self, altitude_setpoint):
        altitude = self.position.z
        hover_thrust = self.DC_gain_z * self.mass * 9.81 

        altitude_error = altitude_setpoint - altitude
        self.altitude_integral += altitude_error * self.quad.dt

        self.altitude_derivative = (altitude_error - self.prev_altitude_error) / self.quad.dt
        self.prev_altitude_error = altitude_error

        thrust = altitude_error * self.Kp_z * self.DC_gain_z + self.altitude_integral * self.Ki_z * self.DC_gain_z + self.altitude_derivative * self.Kd_z * self.DC_gain_z + hover_thrust
    
        return thrust

    def reset(self):
        # Reset integral errors
        self.altitude_integral = 0.0
        self.pitch_integral = 0.0
        self.roll_integral = 0.0

        # Reset previous errors
        self.prev_altitude_error = 0.0
        self.prev_pitch_error = 0.0
        self.prev_roll_error = 0.0
    
        # Reset derivative terms
        self.altitude_derivative = 0.0
        self.pitch_derivative = 0.0
        self.roll_derivative = 0.0

        # Reset setpoints
        self.pitch_setpoint = 0.0
        self.roll_setpoint = 0.0

        # Set current yaw to target
        self.yaw_setpoint = self.quad.attitude.yaw

    def zero(self):
        self._pitch_sum = 0.0
        self._roll_sum = 0.0
        for i in range(0,100):
            self._pitch_sum += self.quad.attitude.pitch
            self._roll_sum += self.quad.attitude.roll
            time.sleep(0.001)
        self.quad.pitch_trim = 1.5 * np.clip(self._pitch_sum/100, -1, 1)
        self.quad.roll_trim = 1.5 * np.clip(self._roll_sum/100, -1, 1)