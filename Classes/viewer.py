from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import math, os, trimesh, functions
from .ModelClasses import ThrustBar, ThrustPanel

#importing quadcopter model (RELATIVE PATH)
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir,"Models","Quadcopter.stl")

#load model and ensure centered
mesh = trimesh.load(model_path)
vertices = mesh.vertices
faces = mesh.faces
center = vertices.mean(axis=0)
vertices -= center

md = gl.MeshData.sphere(rows=10,cols=10)

class DroneViewer(QtWidgets.QWidget,):
    def __init__(self, quadcopter):
        super().__init__()
        self.quadcopter = quadcopter

        # window settings 
        self.setWindowTitle("Quadcopter Client")
        self.resize(1200,800)

        # create and add thrust panel
        self.view = gl.GLViewWidget()
        self.thrust_panel = ThrustPanel()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.view, stretch=3)
        layout.addWidget(self.thrust_panel, stretch=1)

        # initialise camera viewing from behind drone
        self.view.setCameraPosition(
            distance=5,
            elevation=20,
            azimuth=0)

        #create quadcopter model
        self.model = gl.GLMeshItem(
            vertexes = vertices,
            faces = faces,
            smooth = True,
            drawEdges = False,
            color = (0.7,0.7,0.7,1.0),
            shader = 'shaded'
        )

        #create front marker
        self.front_marker = gl.GLMeshItem(
            meshdata = md,
            color=(1, 0, 0, 1),
            smooth=False,
            shader='balloon'
        )

        #add models
        self.view.addItem(self.model)
        self.view.addItem(self.front_marker)

        #render loop
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

        # position front marker in front of the drone
        local = QtGui.QMatrix4x4()
        local.translate(100, -10, 0)
        local.scale(5, 5, 5)
        world = self.model.transform() * local
        self.front_marker.setTransform(world)

        # update thrust in model
        
        thrust = self.quadcopter.controls.thrust

        self.thrust_panel.update(
            total=thrust / 60000 * 100,
            m1=self.quadcopter.thrust[1,0],
            m2=self.quadcopter.thrust[2,0],
            m3=self.quadcopter.thrust[3,0],
            m4=self.quadcopter.thrust[4,0],
        )
