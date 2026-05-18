import numpy as np


class PIDstabiliser():
    def __init__(self, quadcopter):
        self.quad = quadcopter

        self.roll_setpoint = 0.0
        self.pitch_setpoint = 0.0
#        self.yaw_setpoint = 0.0

        self.previous_roll_error = 0.0
        self.previous_pitch_error = 0.0

        self.integral_roll_error = 0.0
        self.integral_pitch_error = 0.0

        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch
#        self.yaw = self.quad.attitude.yaw

        self.hovering = None
        self.max_angle = 5 # max angle change in degrees

        self.Kp_roll_pitch = 1.2
        self.Ki_roll_pitch = 0.3
        self.Kd_roll_pitch = 0.8

        self.attitude_gain = 500

    def hover(self, thrust, dt):
        self.roll = self.quad.attitude.roll
        self.pitch = self.quad.attitude.pitch
        u = np.zeros((4,1))

        roll_error = self.roll_setpoint - self.roll
        pitch_error = self.pitch_setpoint - self.pitch

        self.integral_roll_error += roll_error * dt
        self.integral_pitch_error += pitch_error * dt
        self.integral_roll_error = np.clip(self.integral_roll_error, -self.max_angle, self.max_angle)
        self.integral_pitch_error = np.clip(self.integral_pitch_error, -self.max_angle, self.max_angle)


        roll_cmd = roll_error * self.Kp_roll_pitch + self.integral_roll_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (roll_error - self.previous_roll_error) / max(dt, 1e-5)
        pitch_cmd = pitch_error * self.Kp_roll_pitch + self.integral_pitch_error * self.Ki_roll_pitch + self.Kd_roll_pitch * (pitch_error - self.previous_pitch_error) / max(dt, 1e-5)
        roll_cmd = np.clip(roll_cmd, -self.max_angle, self.max_angle)
        pitch_cmd = np.clip(pitch_cmd, -self.max_angle, self.max_angle)

        roll_cmd *= self.attitude_gain
        pitch_cmd *= self.attitude_gain

        u[0,0] = 0 # yaw
        u[1,0] = pitch_cmd # pitch
        u[2,0] = roll_cmd # roll
        u[3,0] = thrust # thrust

        self.previous_roll_error = roll_error
        self.previous_pitch_error = pitch_error

        return u 

