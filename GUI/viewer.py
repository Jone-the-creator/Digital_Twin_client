from PyQt6 import QtGui
from PyQt6.QtCore import (
    QTimer, QThread, pyqtSignal
)
from PyQt6.QtWidgets import (
    QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout
)
import pyqtgraph.opengl as gl
import os, trimesh
from Classes.ModelClasses import ThrustPanel, ReadingPanel
from GUI.recorder import RecorderWorker

#importing quadcopter model (RELATIVE PATH)
base_dir = os.path.dirname(os.path.dirname(__file__)) # go to project folder
model_path = os.path.join(base_dir,"Classes", "Models", "Quadcopter.stl")

#load model and ensure centered
mesh = trimesh.load(model_path)
vertices = mesh.vertices
faces = mesh.faces
center = vertices.mean(axis=0)
vertices -= center

md = gl.MeshData.sphere(rows=10,cols=10)

class DroneViewer(QWidget,):
    start_record_signal = pyqtSignal()
    stop_record_signal = pyqtSignal()
    def __init__(self, quadcopter):
        super().__init__()
        self.quadcopter = quadcopter

        # window settings 
        self.setWindowTitle("Quadcopter Client")
        self.resize(1200,800)

        # create and add thrust panel
        self.view = gl.GLViewWidget()
        self.thrust_panel = ThrustPanel()
        self.reading_panel = ReadingPanel()
        self.start_recording_btn = QPushButton("Start Recording")
        self.stop_recording_btn = QPushButton("Stop Recording")

        # recording label, shown and hidden based on recording state
        self.recording = QLabel("● Recording")
        self.recording.setStyleSheet("color: red; font-weight: bold;")
        self.recording.hide()  # hidden by default


        layout = QHBoxLayout(self)
        layout.addWidget(self.view, stretch=3)
        layout.addWidget(self.thrust_panel)
        layout.addWidget(self.reading_panel,stretch=1)

        # organises recording GUI
        recording_widget = QWidget()
        recording_layout = QVBoxLayout(recording_widget)
        recording_layout.addStretch()
        recording_layout.addWidget(self.recording)

        button_layout = QHBoxLayout(self)
        button_layout.addWidget(self.start_recording_btn)
        button_layout.addWidget(self.stop_recording_btn)

        recording_layout.addLayout(button_layout)


        layout.addWidget(recording_widget)

        # initialise camera viewing from behind drone
        self.view.setCameraPosition(
            distance=5,
            elevation=20,
            azimuth=0)


        self.base_transform = QtGui.QMatrix4x4()
        self.base_transform.scale(0.01, 0.01, 0.01)
        self.base_transform.rotate(180, 0, 0, 1)
        self.base_transform.rotate(90, 1, 0, 0)
        


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
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_model)
        self.timer.start(16)  # ~60 FPS

        # record data when start recording button pressed
        self.start_recording_btn.clicked.connect(self.start_record)
        self.stop_recording_btn.clicked.connect(self.stop_record)

        self.start_record_signal.connect(self.start_record)
        self.stop_record_signal.connect(self.stop_record)


    # update model from quadcopter object
    def update_model(self):
        roll = self.quadcopter.attitude.roll
        pitch = self.quadcopter.attitude.pitch
        yaw = self.quadcopter.attitude.yaw

                
        transform = QtGui.QMatrix4x4()

        transform.rotate(yaw, 0, 0, 1)

        transform.rotate(pitch, 0, 1, 0)
        transform.rotate(-roll, 1, 0, 0)

        transform = transform * self.base_transform

        self.model.setTransform(transform)


        # position front marker in front of the drone
        local = QtGui.QMatrix4x4()
        local.translate(100, -10, 0)
        local.scale(5, 5, 5)
        world = self.model.transform() * local
        self.front_marker.setTransform(world)

        # update thrust in model
        thrust = self.quadcopter.controls.thrust
        self.thrust_panel.update(thrust / 60000 * 100)

        # update readings
        self.reading_panel.update(
            battery=self.quadcopter.battery_percent,
            battvolt=self.quadcopter.battery_voltage,
            yaw = self.quadcopter.attitude.yaw,
            pitch = self.quadcopter.attitude.pitch,
            roll = self.quadcopter.attitude.roll,
            )
        

    def start_record(self):
    #    if hasattr(self, "thread") and self.thread is not None:
    #        if self.thread.isRunning():
    #            return  # already recording

        # shows recording status
        self.recording.show()

        # creates thread
        self.thread = QThread()
        self.worker = RecorderWorker(self.quadcopter)

        # recorder worker is moved to the thread, can then be run in the background
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.start)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


    def stop_record(self):
        if hasattr(self, "worker"):
            self.recording.hide()
            self.worker.stop()
    
    def closeEvent(self, event):
        if hasattr(self, "worker"):
            self.worker.stop()

        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.wait()

        event.accept()
