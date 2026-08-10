import numpy as np
import state_space as ss

g = 9.81 # m/s^2

class Model:
    def __init__(self, quadcopter):
        self.quad = quadcopter
        self.x = np.array([
            [self.quad.position.x],
            [self.quad.position.y],
            [self.quad.position.z],
            [self.quad.velocity.x],
            [self.quad.velocity.y],
            [self.quad.velocity.z],
            [self.quad.attitude.roll],
            [self.quad.attitude.pitch],
            [self.quad.attitude.yaw],
            [self.quad.velocity.roll],
            [self.quad.velocity.pitch],
            [self.quad.velocity.yaw]
        ])

        self.A = np.array([
            [0, 0, 0, 1, 0, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, -g, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, g,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0]
        ])

        self.B = np.array([
            [0,                0,                0,                0               ],
            [0,                0,                0,                0               ],
            [0,                0,                0,                0               ],
            [0,                0,                0,                0               ],
            [1/self.quad.mass, 0,                0,                0               ],
            [0,                0,                0,                0               ],
            [0,                0,                0,                0               ],
            [0,                0,                0,                0               ],
            [0,                0,                0,                0               ],
            [0,                1/self.quad.I_xx, 0,                0               ],
            [0,                0,                1/self.quad.I_yy, 0               ],
            [0,                0,                0,                1/self.quad.I_zz],

        ])

        self.C = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
        ])

        self.D = np.array([
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])