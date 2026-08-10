# Written by Jonah Habel 2026
# Flinders University

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

    def _write_back(self): 
        self.quad.position.x = float(self.x[0,0])
        self.quad.position.y = float(self.x[1,0])
        self.quad.position.z = float(self.x[2,0])

        self.quad.velocity.x = float(self.x[3,0])
        self.quad.velocity.y = float(self.x[4,0])
        self.quad.velocity.z = float(self.x[5,0])

        self.quad.attitude.roll = float(self.x[6,0])
        self.quad.attitude.pitch = float(self.x[7,0])
        self.quad.attitude.yaw = float(self.x[8,0])

        self.quad.velocity.roll = float(self.x[9,0])
        self.quad.velocity.pitch = float(self.x[10,0])
        self.quad.velocity.yaw = float(self.x[11,0])

    def update(self, u, dt):
        # update state matrix
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

        x_dot = self.A @ self.x + self.B @ u 

        self.x += x_dot * dt

        self._write_back()