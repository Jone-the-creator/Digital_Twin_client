import numpy as np

# pitch and roll trims
pitch_trim = 0
roll_trim = 0

class PIDstabiliser():
    def __init__(self, quadcopter):
        self.quad = quadcopter

        # initialise setpoints, adjust these directly for control
        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
#        self.yaw_setpoint = 0.0

        # previous errors for derivative error
        self.previous_roll_error = 0.0
        self.previous_pitch_error = 0.0

        # integral errors
        self.integral_roll_error = 0.0
        self.integral_pitch_error = 0.0

        # initialise current attitude readings
        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch
#        self.yaw = self.quad.attitude.yaw

        # maximum angle change to remain within linear approximation (small angle change)
        self.max_angle = 5 # in degrees

        # max integral term (limit integral windup)
        self.max_int = 50 

        # PID gains
        self.Kp_roll_pitch = 1.48
        self.Ki_roll_pitch = 0.45
        self.Kd_roll_pitch = 1.02

    # hover mode, with a thrust given and dt this will just hover and apply a thrust
    def hover(self, thrust, dt):
        # update attitude angles from quadcopter object
        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch

        # initialise control array
        u = np.zeros((4,1))

        # calculate attitude errors
        roll_error = self.roll_setpoint - self.roll
        pitch_error = self.pitch_setpoint - self.pitch

        # calculate integral errors and clip them
        self.integral_roll_error += roll_error * dt
        self.integral_pitch_error += pitch_error * dt
        self.integral_roll_error = np.clip(self.integral_roll_error, -self.max_int, self.max_int)
        self.integral_pitch_error = np.clip(self.integral_pitch_error, -self.max_int, self.max_int)

        # pitch and roll commands calculated with PID
        roll_cmd = roll_error * self.Kp_roll_pitch + self.integral_roll_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (roll_error - self.previous_roll_error) / max(dt, 1e-5)
        pitch_cmd = pitch_error * self.Kp_roll_pitch + self.integral_pitch_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (pitch_error - self.previous_pitch_error) / max(dt, 1e-5)
        roll_cmd = np.clip(roll_cmd, -self.max_angle, self.max_angle)
        pitch_cmd = np.clip(pitch_cmd, -self.max_angle, self.max_angle)

        u[0,0] = 0 # yaw
        u[1,0] = -pitch_cmd + pitch_trim # pitch
        u[2,0] = roll_cmd + roll_trim # roll
        u[3,0] = thrust # thrust

        # save previous error for next derivative error
        self.previous_roll_error = roll_error
        self.previous_pitch_error = pitch_error

        return u 

