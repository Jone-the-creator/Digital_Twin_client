import numpy as np

class PIDstabiliser():
    def __init__(self, quadcopter):
        self.quad = quadcopter
        
        self.pitch_trim = 0.0
        self.roll_trim = 0.0
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
        self.integral_z_error = 0.0

        # initialise current attitude readings
        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch
#        self.yaw = self.quad.attitude.yaw

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 5 # in degrees

        # max integral term (limit integral windup)
        self.max_int = 50 

        # PID gains
        self.K_roll_pitch = 25.0
        self.Kp_roll_pitch = 1
        self.Ki_roll_pitch = 0.5
        self.Kd_roll_pitch = 0.25
        self.K_z = 3000 # thrust DC gain 
        self.Kp_z = 1.5
        self.Ki_z = 0
        self.Kd_z = 0

    # hover mode, with a thrust given and dt this will just hover and apply a thrust
    def hover(self, z, dt):
        if not self.quad.killed:
            # update attitude angles from quadcopter object
            self.roll = self.quad.attitude.roll
            self.pitch = self.quad.attitude.pitch

            # update positions from quadcopter object
            self.z = self.quad.position.z

            # # update trim on start of hover mode
            # pitch_trim = self.pitch
            # roll_trim = self.roll

            # initialise control array
            u = np.zeros((4,1))

            # calculate attitude errors
            roll_error = self.roll_setpoint - (self.roll - self.roll_trim)
            pitch_error = self.pitch_setpoint - (self.pitch - self.pitch_trim)

            # calculate z error
            z_error = z - (self.z - self.z_trim)

            # calculate integral errors and clip them
            self.integral_roll_error += roll_error * dt
            self.integral_pitch_error += pitch_error * dt
            self.integral_z_error += z_error * dt
            self.integral_roll_error = np.clip(self.integral_roll_error, -self.max_int, self.max_int)
            self.integral_pitch_error = np.clip(self.integral_pitch_error, -self.max_int, self.max_int)
            self.integral_z_error = np.clip(self.integral_z_error, -self.max_int, self.max_int)

            # pitch and roll commands calculated with PID
            roll_cmd = self.K_roll_pitch * (roll_error * self.Kp_roll_pitch + self.integral_roll_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (roll_error - self.previous_roll_error) / dt )
            pitch_cmd = self.K_roll_pitch* (pitch_error * self.Kp_roll_pitch + self.integral_pitch_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (pitch_error - self.previous_pitch_error) / dt)

            # thrust command calculated with PID
            thrust = self.K_z*(z_error * self.Kp_z + self.integral_z_error * self.Ki_z) # + (z_error - self.previous_z_error) / max(dt, 1e-5) * self.Kd_z
            
            # print(f"pitch = {self.quad.attitude.pitch}, roll = {self.quad.attitude.roll}")
            # print(f"pitch rate = {pitch_cmd}, roll rate = {roll_cmd}")
            u[0,0] = 0 # yaw
            u[1,0] = pitch_cmd # pitch
            u[2,0] = roll_cmd # roll
            u[3,0] = thrust # thrust

            # save previous error for next derivative error
            self.previous_roll_error = roll_error
            self.previous_pitch_error = pitch_error
            self.previous_z_error = z_error

            return u 

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
