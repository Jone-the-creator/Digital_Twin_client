# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot
# main_window.py
# -- used to instantiate and control imported main window UI from the designer --

from PySide6 import QtGui
from PySide6.QtCore import (
    QTimer, QThread, Signal
)
from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QMainWindow, QLabel, QVBoxLayout
)
import pyqtgraph.opengl as gl
import os, trimesh
import numpy as np
from Classes.recorder import RecorderWorker
from GUI.ui.ui_main import Ui_MainWindow
from scipy.signal import place_poles

# importing quadcopter model (RELATIVE PATH)
base_dir = os.path.dirname(os.path.dirname(__file__)) # go to project folder
model_path = os.path.join(base_dir, "Models", "Quadcopter.stl")

# load model and ensure centered
mesh = trimesh.load(model_path)
vertices = mesh.vertices
faces = mesh.faces
center = vertices.mean(axis=0)
vertices -= center

md = gl.MeshData.sphere(rows=10,cols=10)

class MainWindow(QMainWindow):
    start_record_signal = Signal()
    stop_record_signal = Signal()
    def __init__(self, quadcopter, stabiliser):
        super().__init__()
        self.quadcopter = quadcopter
        self.stab = stabiliser
        
        # instantiate ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # OpenGL view inside placeholder
        self.view = gl.GLViewWidget()

        layout = QVBoxLayout(self.ui.gl_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.ui.controller_select.addItems([
            "Attitude Controller",
            "Altitude Controller"
        ])


        # grid settings
        self.grid = gl.GLGridItem()
        self.grid.scale(1, 1, 1)
        self.grid.setSize(10, 10)
        self.grid.setSpacing(0.5, 0.5)

        # axes
        self.x_axis = gl.GLLinePlotItem(
            pos=np.array([[0,0,0],[2,0,0]]),
            color=(1,0,0,1),
            width=3
        )

        self.y_axis = gl.GLLinePlotItem(
            pos=np.array([[0,0,0],[0,2,0]]),
            color=(0,1,0,1),
            width=3
        )

        self.z_axis = gl.GLLinePlotItem(
            pos=np.array([[0,0,0],[0,0,2]]),
            color=(0,0,1,1),
            width=3
        )

        self.ui.recording_label.hide()  # hidden by default

        # initialise camera viewing from behind drone
        self.view.setCameraPosition(
            distance=5,
            elevation=20,
            azimuth=0)


        self.base_transform = QtGui.QMatrix4x4()
        self.base_transform.translate(0, 0, 0.2) # STL units
        self.base_transform.scale(0.005, 0.005, 0.005)
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

        # add models
        self.view.addItem(self.grid)
        self.view.addItem(self.model)
        self.view.addItem(self.front_marker)
        self.view.addItem(self.x_axis)
        self.view.addItem(self.y_axis)
        self.view.addItem(self.z_axis)

        # Control tuning
        if self.quadcopter.control_system == "Pole-placement":
            self.ui.title.setText("Pole-placement Tuning")

            # hide all tuning for PID
            self.ui.D_label.hide()
            self.ui.d_add_large.hide()
            self.ui.d_add_small.hide()
            self.ui.d_sub_large.hide()
            self.ui.d_sub_small.hide()

            # change buttons for PP
            self.ui.p_add_large.setText("+0.25s")
            self.ui.p_add_small.setText("+0.05s")
            self.ui.p_sub_large.setText("-0.25s")
            self.ui.p_sub_small.setText("-0.05s")
            self.ui.i_add_large.setText("+1.0%")
            self.ui.i_add_small.setText("+0.25%")
            self.ui.i_sub_large.setText("-1.0%")
            self.ui.i_sub_small.setText("-0.25%")

            self.update_PP_labels(
                self.stab.settling_time_z,
                self.stab.overshoot_z
            )

        elif self.quadcopter.control_system == "PID":
            self.ui.title.setText("PID Tuning")
            self.update_pid_labels(
                self.stab.Kp_att,
                self.stab.Ki_att,
                self.stab.Kd_att
            )

        # render loop
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_model)
        self.render_timer.start(16)  # ~60 FPS

        # data update loop
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_GUI)
        self.data_timer.start(50)  # ~20 FPS

        # record data when start recording button pressed
        self.ui.start_recording_btn.clicked.connect(self.start_record)
        self.ui.stop_recording_btn.clicked.connect(self.stop_record)


        if self.quadcopter.control_system == "PID":
            # connect buttons to change gains
            # P gains
            self.ui.p_sub_large.clicked.connect(lambda: self.handle_pid_change("P", -0.25))
            self.ui.p_sub_small.clicked.connect(lambda: self.handle_pid_change("P", -0.05))
            self.ui.p_add_small.clicked.connect(lambda: self.handle_pid_change("P", 0.05))
            self.ui.p_add_large.clicked.connect(lambda: self.handle_pid_change("P", 0.25))

            # I gains
            self.ui.i_sub_large.clicked.connect(lambda: self.handle_pid_change("I", -0.25))
            self.ui.i_sub_small.clicked.connect(lambda: self.handle_pid_change("I", -0.05))
            self.ui.i_add_small.clicked.connect(lambda: self.handle_pid_change("I", 0.05))
            self.ui.i_add_large.clicked.connect(lambda: self.handle_pid_change("I", 0.25))

            # D gains
            self.ui.d_sub_large.clicked.connect(lambda: self.handle_pid_change("D", -0.25))
            self.ui.d_sub_small.clicked.connect(lambda: self.handle_pid_change("D", -0.05))
            self.ui.d_add_small.clicked.connect(lambda: self.handle_pid_change("D", 0.05))
            self.ui.d_add_large.clicked.connect(lambda: self.handle_pid_change("D", 0.25))

        elif self.quadcopter.control_system == "Pole-placement":
            # connect buttons to change specs
            # Settling time
            self.ui.p_sub_large.clicked.connect(lambda: self.handle_spec_change("Tss", -0.25))
            self.ui.p_sub_small.clicked.connect(lambda: self.handle_spec_change("Tss", -0.05))
            self.ui.p_add_small.clicked.connect(lambda: self.handle_spec_change("Tss", 0.05))
            self.ui.p_add_large.clicked.connect(lambda: self.handle_spec_change("Tss", 0.25))

            # Overshoot
            self.ui.i_sub_large.clicked.connect(lambda: self.handle_spec_change("Mp", -1.0))
            self.ui.i_sub_small.clicked.connect(lambda: self.handle_spec_change("Mp", -0.25))
            self.ui.i_add_small.clicked.connect(lambda: self.handle_spec_change("Mp", 0.25))
            self.ui.i_add_large.clicked.connect(lambda: self.handle_spec_change("Mp", 1.0))

        self.start_record_signal.connect(self.start_record)
        self.stop_record_signal.connect(self.stop_record)

        # switch between simulation and real plant when simulation button pressed
        self.ui.sim_btn.clicked.connect(self.toggle_simulation)


    # update model from quadcopter object
    def update_model(self):
        roll = self.quadcopter.attitude.roll
        pitch = self.quadcopter.attitude.pitch
        yaw = self.quadcopter.attitude.yaw
        x = self.quadcopter.position.x
        y = self.quadcopter.position.y
        z = self.quadcopter.position.z

        self.view.opts["center"].setX(x)
        self.view.opts["center"].setY(y)
        self.view.opts["center"].setZ(z)
                
        transform = QtGui.QMatrix4x4()

        transform.translate(x, y, z)

        transform.rotate(yaw, 0, 0, 1)
        transform.rotate(-pitch, 0, 1, 0)
        transform.rotate(-roll, 1, 0, 0)

        transform *= self.base_transform

        self.model.setTransform(transform)


        # position front marker in front of the drone
        local = QtGui.QMatrix4x4()
        local.translate(100, -10, 0)
        local.scale(5, 5, 5)
        world = self.model.transform() * local
        self.front_marker.setTransform(world)

    def update_GUI(self):
        # update thrust variable (currently unused)
        thrust = ((self.quadcopter.controls.thrust / self.quadcopter.max_thrust) * 100)
        
        if self.quadcopter.battery_percent is not None:
            self.ui.battery_bar.setValue(
                int(self.quadcopter.battery_percent)
            )

        # update readings
        self.ui.yaw_reading.setText(f"Yaw: {self.quadcopter.attitude.yaw:.2f} °")
        self.ui.pitch_reading.setText(f"Pitch: {self.quadcopter.attitude.pitch:.2f} °")
        self.ui.roll_reading.setText(f"Roll: {self.quadcopter.attitude.roll:.2f} °")
        self.ui.altitude_reading.setText(f"Current Altitude: {self.quadcopter.position.z:.2f} m")
        self.ui.altitude_sp_reading.setText(f"Altitude Setpoint: {self.quadcopter.controls.z:.2f} m")
        self.ui.loop_rate_reading.setText(f"Loop Rate: {self.quadcopter.loop_rate:.1f} Hz")
        controller = self.ui.controller_select.currentText().lower()

        if self.quadcopter.control_system == "Pole-placement":
            self.update_PP_labels(
                self.stab.settling_time_z,
                self.stab.overshoot_z
            )

        elif self.quadcopter.control_system == "PID":
            if controller == "altitude controller":
                self.update_pid_labels(
                    self.stab.Kp_z,
                    self.stab.Ki_z,
                    self.stab.Kd_z
                )
            else:
                self.update_pid_labels(
                    self.stab.Kp_att,
                    self.stab.Ki_att,
                    self.stab.Kd_att
                )

    def start_record(self):
        # shows recording status
        self.ui.recording_label.show()

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
            self.ui.recording_label.hide()
            self.worker.stop()

        if hasattr(self, "thread"):
            self.thread.requestInterruption() 
            self.thread.quit()
            self.thread.wait()

    def handle_pid_change(self, gain, delta):
        controller = self.ui.controller_select.currentText().lower()
        if controller == "altitude controller":
            if gain == "P":
                self.stab.Kp_z += delta
            elif gain == "I":
                self.stab.Ki_z += delta
            elif gain == "D":
                self.stab.Kd_z += delta
            self.update_pid_labels(
                self.stab.Kp_z,
                self.stab.Ki_z,
                self.stab.Kd_z
            )
        else:
            if gain == "P":
                self.stab.Kp_att += delta
            elif gain == "I":
                self.stab.Ki_att += delta
            elif gain == "D":
                self.stab.Kd_att += delta
            self.update_pid_labels(
                self.stab.Kp_att,
                self.stab.Ki_att,
                self.stab.Kd_att
            )

    def handle_spec_change(self, spec, delta):
        controller = self.ui.controller_select.currentText().lower()
        if controller == "altitude controller":
            if spec == "Tss":
                self.stab.settling_time_z += delta
            elif spec == "Mp":
                self.stab.overshoot_z += delta
            self.update_PP_labels(
                self.stab.settling_time_z,
                self.stab.overshoot_z
            )

        # -- adjust poles/gains based on new specifications --
        self.stab.zeta_z = np.sqrt(((np.log(self.stab.overshoot_z/100))**2)/(np.pi**2+(np.log(self.stab.overshoot_z/100))**2))
        self.stab.omega_z = 4/(self.stab.zeta_z*self.stab.settling_time_z)
     
        # calculate poles based on adjustable specifications
        self.stab.desired_poles = np.array([-self.stab.zeta_z*self.stab.omega_z * 100, 
                                -self.stab.zeta_z*self.stab.omega_z + (self.stab.omega_z*np.sqrt(1-self.stab.zeta_z**2))*1j, 
                                -self.stab.zeta_z*self.stab.omega_z - (self.stab.omega_z*np.sqrt(1-self.stab.zeta_z**2))*1j 
                                ])


        self.stab.K_z = place_poles(self.stab.A, self.stab.B, self.stab.desired_poles).gain_matrix
        print(self.stab.K_z)

    def toggle_simulation(self):
        self.quadcopter.simulation_mode = (
            not self.quadcopter.simulation_mode
        )

        if self.quadcopter.simulation_mode:
            self.ui.sim_btn.setText("Simulation: ON")
            # reset all attitudes for simulation
            self.quadcopter.attitude.yaw = 0.0
            self.quadcopter.attitude.pitch = 0.0
            self.quadcopter.attitude.roll = 0.0
        else:
            self.ui.sim_btn.setText("Simulation: OFF")

    def update_pid_labels(self, kp, ki, kd):
        self.ui.P_label.setText(f"P: {kp:.2f}")
        self.ui.I_label.setText(f"I: {ki:.2f}")
        self.ui.D_label.setText(f"D: {kd:.2f}")

    def update_PP_labels(self, Tss, Mp):
        self.ui.P_label.setText(f"Settling time: {Tss:.2f} s")
        self.ui.I_label.setText(f"Overshoot: {Mp:.2f} %")