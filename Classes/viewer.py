from PyQt6 import QtWidgets, QtCore
import pyqtgraph.opengl as gl
import numpy as np
import math
import trimesh
from .ModelClasses import ThrustBar, ThrustPanel
import os

#importing quadcopter model (RELATIVE PATH)
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir,"Models","Quadcopter.stl")

#load model and ensure centered
mesh = trimesh.load(model_path)
vertices = mesh.vertices
faces = mesh.faces
center = vertices.mean(axis=0)
vertices -= center

class DroneViewer(QtWidgets.QWidget,):
    def __init__(self, quadcopter):
        super().__init__()
        self.quadcopter = quadcopter

        # window settings 
        self.setWindowTitle("Quadcopter 3D Model")
        self.resize(1200,800)

        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(
            distance=5,
            elevation=20,
            azimuth=45)
        self.thrust_panel = ThrustPanel()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.view, stretch=3)
        layout.addWidget(self.thrust_panel, stretch=1)


        self.model = gl.GLMeshItem(
            vertexes = vertices,
            faces = faces,
            smooth = True,
            drawEdges = False,
            color = (0.7,0.7,0.7,1.0),
            shader = 'shaded'
        )
        self.view.addItem(self.model)

        # Timer → render loop
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_model)
        self.timer.start(16)  # ~60 FPS


    # update model from quadcopter object
    def update_model(self):
        roll = self.quadcopter.attitude.roll
        pitch = self.quadcopter.attitude.pitch
        yaw = self.quadcopter.attitude.yaw

        self.model.resetTransform()

        # fixed transform (reapply each time)
        self.model.scale(0.01, 0.01, 0.01)
        self.model.rotate(90,1,0,0)
        self.model.rotate(-180,0,0,1)

        # live transform (based on received data)
        self.model.rotate(yaw, 0, 0, 1)     # Z
        self.model.rotate(pitch, 0, 1, 0)   # Y
        self.model.rotate(-roll, 1, 0, 0)    # X
