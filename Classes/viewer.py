from PyQt6 import QtWidgets, QtCore
import pyqtgraph.opengl as gl
import numpy as np
import math
from .ModelClasses import ThrustBar, ThrustPanel

class DroneViewer(QtWidgets.QWidget,):
    def __init__(self, quadcopter):
        super().__init__()
        self.quadcopter = quadcopter

        # window settings 
        self.setWindowTitle("Quadcopter 3D Model")
        self.resize(1200,800)

        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=5)
        self.thrust_panel = ThrustPanel()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.view, stretch=3)
        layout.addWidget(self.thrust_panel, stretch=1)


        self.model = self.create_drone_model()
        self.view.addItem(self.model)

        # Timer → render loop
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_model)
        self.timer.start(16)  # ~60 FPS

    def create_drone_model(self):
        # Simple cross (replace later with mesh)
        pts = np.array([
            [-1, 0, 0], [1, 0, 0],
            [0, -1, 0], [0, 1, 0]
        ])
        lines = gl.GLLinePlotItem(
            pos=pts,
            mode="lines",
            width=3,
            color=(1, 1, 1, 1)
        )
        return lines

    # update model from quadcopter object
    def update_model(self):
        roll = self.quadcopter.attitude.roll
        pitch = self.quadcopter.attitude.pitch
        yaw = self.quadcopter.attitude.yaw

        self.model.resetTransform()
        self.model.rotate(yaw, 0, 0, 1)     # Z
        self.model.rotate(pitch, 0, 1, 0)   # Y
        self.model.rotate(roll, 1, 0, 0)    # X
