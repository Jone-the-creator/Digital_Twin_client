import numpy as np

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
#        self.yaw = self.quad.attitude.yaw

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 5 # in degrees

        # max integral term (limit integral windup)
        self.max_int = 40

    # hover mode, will control attitude with 0 setpoints
    def hover(self, altitude_setpoint, dt):
        # --- ALTITUDE CONTROL ---
        DC_gain_z = 13000.0
        altitude = self.quad.position.z
        hover_thrust = DC_gain_z * self.quad.mass * 9.81 

        altitude_error = altitude_setpoint - altitude
        self.altitude_integral += altitude_error * dt
        self.altitude_integral = np.clip(self.altitude_integral, -self.max_int, self.max_int)
        self.altitude_derivative = (altitude_error - self.prev_altitude_error) / dt
        self.prev_altitude_error = altitude_error

        Kp_z = DC_gain_z * 2.0
        Ki_z = DC_gain_z * 0.1
        Kd_z = DC_gain_z * 0.5

        thrust = altitude_error * Kp_z + self.altitude_integral * Ki_z + self.altitude_derivative * Kd_z + hover_thrust

        # # --- ATTITUDE CONTROL ---
        Kp_att = 2.5
        Ki_att = 0.2
        Kd_att = 0.75

        # Calculate attitude errors
        pitch_error = -np.clip(self.pitch_setpoint - (self.quad.attitude.pitch - self.quad.pitch_trim), -self.max_angle, self.max_angle)
        roll_error = np.clip(self.roll_setpoint - (self.quad.attitude.roll - self.quad.roll_trim), -self.max_angle, self.max_angle)

        self.pitch_integral += pitch_error * dt
        self.roll_integral += roll_error * dt
        self.pitch_integral = np.clip(self.pitch_integral, -self.max_int, self.max_int)
        self.roll_integral = np.clip(self.roll_integral, -self.max_int, self.max_int)

        self.pitch_derivative = pitch_error - self.prev_pitch_error 
        self.roll_derivative = roll_error - self.prev_roll_error
        self.prev_pitch_error = pitch_error
        self.prev_roll_error = roll_error

        # Pitch and roll rate commands calculated with PID based on error in x and y (assuming constant yaw)
        pitch_rate = pitch_error * Kp_att + self.pitch_integral * Ki_att + self.pitch_derivative * Kd_att
        roll_rate = roll_error * Kp_att + self.roll_integral * Ki_att + self.roll_derivative * Kd_att

        # print(f"pitch_error = {pitch_error:.2f} "
        # f"pitch = {self.quad.attitude.pitch:.2f} "
        # f"pitch_rate = {pitch_rate:.2f}")

        # print(f"pitch = {self.quad.attitude.pitch}, roll = {self.quad.attitude.roll}")
        # print(f"pitch rate = {pitch_cmd}, roll rate = {roll_cmd}")

        return pitch_rate, roll_rate, thrust
        
    def altitude_control(self, altitude_setpoint, dt):
        DC_gain = 13000.0
        altitude = self.position.z
        hover_thrust = DC_gain * self.mass * 9.81 

        altitude_error = altitude_setpoint - altitude
        self.altitude_integral += altitude_error * dt

        self.altitude_derivative = (altitude_error - self.prev_altitude_error) / dt
        self.prev_altitude_error = altitude_error

        Kp = DC_gain * 2
        Ki = DC_gain * 0.
        Kd = DC_gain * 0.5

        thrust = altitude_error * Kp + self.altitude_integral * Ki + self.altitude_derivative * Kd + hover_thrust
    
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

    def zero(self):
        self.z_trim = 0.2
        self.roll_trim = 0
        self.pitch_trim = 0
        self.z_trim = self.quad.position.z
        self.roll_trim = self.quad.attitude.roll
        self.pitch_trim = self.quad.attitude.pitch
