import numpy as np
import state_space as ss
from quadcopter import Quadcopter

g = 9.81 # m/s^2

class Model:
    def __init__(self, quad):
        self.x = np.array([
            [quad.position.x],
            [quad.position.y],
            [quad.position.z],
            [quad.velocity.x],
            [quad.velocity.y],
            [quad.velocity.z],
            [quad.attitude.roll],
            [quad.attitude.pitch],
            [quad.attitude.yaw],
            [quad.velocity.roll],
            [quad.velocity.pitch],
            [quad.velocity.yaw]
        ])

        self.A = np.array([
            [0, 0, 0, 1, 0, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, -g, 0, 0, 0, 0]
        ])

        self.B = np.array([
            []
        ])

        self.C = np.array([
            []
        ])

        self.D = np.array([
            []
        ])