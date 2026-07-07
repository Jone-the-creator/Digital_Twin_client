altitude_integral = 0.0

def altitude_control(altitude_setpoint, quad, dt):
    altitude = quad.position.z

    altitude_error = altitude_setpoint - altitude
    altitude_integral += altitude_error * dt

    Kp = 1.0
    Ki = 0.3
    Kd = 0.8

    thrust = altitude_error * Kp + altitude_integral * Ki
    
    return thrust