import numpy as np

class PIDstabiliser():
    def __init__(self, quadcopter):
        self.quad = quadcopter
        

        self.z_trim = 0.0

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
#        self.yaw_setpoint = 0.0

        # previous errors for derivative error
        self.previous_roll_error = 0.0
        self.previous_pitch_error = 0.0
        self.previous_z_error = 0.0

        # integral errors
        self.integral_roll_error = 0.0
        self.integral_pitch_error = 0.0
        self.integral_x_error = 0.0
        self.integral_y_error = 0.0

        # Altitude error variables
        self.altitude_integral = 0.0
        self.prev_altitude_error = 0.0
        self.altitude_derivative = 0.0

        # initialise current attitude readings
        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch
        self.pitch_trim = self.pitch
        self.roll_trim = self.roll
#        self.yaw = self.quad.attitude.yaw

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 2 # in degrees

        # max integral term (limit integral windup)
        self.max_int = 50 

        # PID gains
        self.K_roll_pitch = 100.0
        self.Kp_roll_pitch = 1.0
        self.Ki_roll_pitch = 0.0
        self.Kd_roll_pitch = 0.1
        # self.K_z = 3000 # thrust DC gain 
        # self.Kp_z = 1.5
        # self.Ki_z = 0
        # self.Kd_z = 0

    # hover mode, will control attitude with 0 setpoints
    def hover(self, altitude_setpoint, x_setpoint, y_setpoint, dt):
        # --- ALTITUDE CONTROL ---
        DC_gain_z = 13000.0
        altitude = self.position.z
        hover_thrust = DC_gain_z * self.quad.mass * 9.81 

        altitude_error = altitude_setpoint - altitude
        self.altitude_integral += altitude_error * dt

        self.altitude_derivative = (altitude_error - self.prev_altitude_error) / dt
        self.prev_altitude_error = altitude_error

        Kp = DC_gain_z * 2
        Ki = DC_gain_z * 0.1
        Kd = DC_gain_z * 0.5

        thrust = altitude_error * Kp + self.altitude_integral * Ki + self.altitude_derivative * Kd + hover_thrust

        return thrust

        # # --- ATTITUDE CONTROL ---
        # DC_gain_att = 100.0
        # x = self.position.x
        # y = self.position.y
    
        # if not self.quad.killed:
        #     # update attitude angles from quadcopter object
        #     self.roll = self.quad.attitude.roll
        #     self.pitch = self.quad.attitude.pitch

        #     # calculate attitude errors
        #     roll_error = 0.0 - (self.roll - self.roll_trim)
        #     pitch_error = 0.0 - (self.pitch - self.pitch_trim)

        #     # calculate integral errors and clip them
        #     self.integral_roll_error += roll_error * dt
        #     self.integral_pitch_error += pitch_error * dt
        #     self.integral_roll_error = np.clip(self.integral_roll_error, -self.max_int, self.max_int)
        #     self.integral_pitch_error = np.clip(self.integral_pitch_error, -self.max_int, self.max_int)


        #     # pitch and roll commands calculated with PID
        #     roll_cmd = roll_error * self.Kp_roll_pitch + self.integral_roll_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (roll_error - self.previous_roll_error) / dt 
        #     pitch_cmd = pitch_error * self.Kp_roll_pitch + self.integral_pitch_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (pitch_error - self.previous_pitch_error) / dt

        #     # print(f"pitch = {self.quad.attitude.pitch}, roll = {self.quad.attitude.roll}")
        #     # print(f"pitch rate = {pitch_cmd}, roll rate = {roll_cmd}")

        #     # save previous error for next derivative error
        #     self.previous_roll_error = roll_error
        #     self.previous_pitch_error = pitch_error

        #     return pitch_cmd, roll_cmd, thrust
        
    def altitude_control(self, altitude_setpoint, dt):
        DC_gain = 13000.0
        altitude = self.position.z
        hover_thrust = DC_gain * self.mass * 9.81 

        altitude_error = altitude_setpoint - altitude
        self.altitude_integral += altitude_error * dt

        self.altitude_derivative = (altitude_error - self.prev_altitude_error) / dt
        self.prev_altitude_error = altitude_error

        Kp = DC_gain * 2
        Ki = DC_gain * 0.1
        Kd = DC_gain * 0.5

        thrust = altitude_error * Kp + self.altitude_integral * Ki + self.altitude_derivative * Kd + hover_thrust
    
        return thrust

    def reset(self):
        # reset integral errors
        self.integral_pitch_error = 0.0
        self.integral_roll_error = 0.0
        self.integral_z_error = 0.0

        # reset previous errors
        self.previous_pitch_error = 0.0
        self.previous_roll_error = 0.0
        self.previous_z_error = 0.0

    def zero(self):
        self.z_trim = 0.2
        self.roll_trim = 0
        self.pitch_trim = 0
        self.z_trim = self.quad.position.z
        self.roll_trim = self.quad.attitude.roll
        self.pitch_trim = self.quad.attitude.pitch
