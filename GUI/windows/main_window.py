# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot
# main_window.py
# -- used to instantiate and control imported main window UI from the designer --

from PySide6 import QtGui
from PySide6.QtGui import QCursor
from PySide6.QtCore import (
    QTimer, QThread, Signal, Qt
)
from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QMainWindow, QLabel, QVBoxLayout
)
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import os, trimesh, time
import numpy as np
from Classes.recorder import RecorderWorker
from GUI.ui.ui_main import Ui_MainWindow
from scipy.signal import place_poles
from GUI.windows.calibration_window import CalibrationWindow

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
    def __init__(self, quadcopter, stabiliser, obs, sim_non_linear, sim_linear, sim_1, sim_2):
        super().__init__()
        self.quadcopter = quadcopter
        self.stab = stabiliser
        self.obs = obs
        self.sim_non_linear = sim_non_linear
        self.sim_linear = sim_linear
        self.sim_1 = sim_1
        self.sim_2 = sim_2
        self.cal = None

        self.response_time = []
        self.response_altitude = []
        self.response_setpoint = []
        self.logging_response = False

        self.step_start_time = time.time()
        
        # instantiate ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Step response plot
        self.response_plot = pg.PlotWidget()

        self.response_plot.setLabel('left', 'Altitude (m)')
        self.response_plot.setLabel('bottom', 'Time (s)')
        self.response_plot.showGrid(x=True, y=True)
        self.response_plot.addLegend()

        layout = QVBoxLayout(self.ui.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.response_plot)

        self.alt_curve = self.response_plot.plot(
            pen='y',
            name='Altitude'
        )

        self.sp_curve = self.response_plot.plot(
            pen='r',
            name='Setpoint'
        )

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
        self.grid.setSize(100, 100)
        self.grid.setSpacing(0.5, 0.5)

        # alarms/warnings hidden by default
        self.ui.recording_label.hide()
        self.ui.Warn_alarm.hide()
        self.ui.Warn_thrust_alarm.hide() 

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

        # CREATE PHYSICAL PLANT MODEL
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

        # CREATE SIMULATION PLANT MODEL
        #create quadcopter model
        self.digital_twin = gl.GLMeshItem(
            vertexes=vertices,
            faces=faces,
            smooth=True,
            drawEdges=True,
            edgeColor=(0.2, 0.7, 0.9, 0.5),
            color=(0.0, 0.25, 0.65, 0.15),
            shader='balloon'
        )

        self.model.setGLOptions('translucent')

        #create front marker
        self.DT_front_marker = gl.GLMeshItem(
            meshdata = md,
            color=(0.0, 0.25, 0.65, 0.8),
            smooth=False,
            shader='balloon'
        )

        # add models
        self.view.addItem(self.grid)
        self.view.addItem(self.model)
        self.view.addItem(self.front_marker)
        self.view.addItem(self.digital_twin)
        self.view.addItem(self.DT_front_marker)
        self.digital_twin.hide()
        self.DT_front_marker.hide()

        self.ui.model_select.addItems(["Non-linear Model", "Linearised Model"])

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
        self.render_timer.timeout.connect(self.update_DT)
        self.render_timer.timeout.connect(self.update_model)
        self.render_timer.timeout.connect(self.update_camera)
        self.render_timer.start(10) # 100 Hz

        # data update loop
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_GUI)
        self.data_timer.start(50)  # ~20 FPS

        # record data when start recording button pressed
        self.ui.start_recording_btn.clicked.connect(self.start_record)
        self.ui.stop_recording_btn.clicked.connect(self.stop_record)

        # open calibration window upon button press
        self.ui.calibrate_button.clicked.connect(self.calibration_window)


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
        self.ui.DT_btn.clicked.connect(self.toggle_DT)


    # update model from quadcopter object
    def update_model(self):
        roll = self.quadcopter.attitude.roll
        pitch = self.quadcopter.attitude.pitch
        yaw = self.quadcopter.attitude.yaw
        x = self.quadcopter.position.x
        y = self.quadcopter.position.y
        z = self.quadcopter.position.z

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

    # update Digital Twin from quadcopter object
    def update_DT(self):
        roll = self.sim_linear.attitude.roll
        pitch = self.sim_linear.attitude.pitch
        yaw = self.sim_linear.attitude.yaw
        x = self.sim_linear.position.x
        y = self.sim_linear.position.y
        z = self.sim_linear.position.z
                
        transform = QtGui.QMatrix4x4()

        transform.translate(x, y, z)

        transform.rotate(yaw, 0, 0, 1)
        transform.rotate(-pitch, 0, 1, 0)
        transform.rotate(-roll, 1, 0, 0)

        transform *= self.base_transform

        self.digital_twin.setTransform(transform)

        # position front marker in front of the drone
        local = QtGui.QMatrix4x4()
        local.translate(100, -10, 0)
        local.scale(5, 5, 5)
        world = self.digital_twin.transform() * local
        self.DT_front_marker.setTransform(world)

    def update_camera(self):
        if self.quadcopter.simulation_mode:
            # Follow simulated model

            if self.ui.model_select.currentText().lower() == "non-linear model":
                x = self.sim_non_linear.position.x
                y = self.sim_non_linear.position.y
                z = self.sim_non_linear.position.z
            else:
                x = self.sim_linear.position.x
                y = self.sim_linear.position.y
                z = self.sim_linear.position.z

        else:
            # Normal operation and DT mode
            x = self.quadcopter.position.x
            y = self.quadcopter.position.y
            z = self.quadcopter.position.z

        self.view.opts["center"].setX(x)
        self.view.opts["center"].setY(y)
        self.view.opts["center"].setZ(z)

    def update_GUI(self):
        # update thrust variable (currently unused)
        thrust = ((self.quadcopter.controls.thrust / self.quadcopter.max_thrust) * 100)
        
        if self.quadcopter.battery_percent is not None:
            self.ui.battery_bar.setValue(
                int(self.quadcopter.battery_percent)
            )

        if self.quadcopter.hover_thrust == 38000:
            self.ui.Warn_thrust_alarm.show()
        else:
            self.ui.Warn_thrust_alarm.hide()

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
        self.update_step_response()

    def start_record(self):
        # shows recording status
        self.ui.recording_label.show()

        # block adjustment of recording rate
        self.ui.Recording_rate_adj.setReadOnly(1)
        self.ui.Recording_rate_adj.setCursor(QCursor(Qt.CursorShape.ForbiddenCursor))

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
        # allow adjustment of recording rate
        self.ui.Recording_rate_adj.setReadOnly(0)
        self.ui.Recording_rate_adj.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

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

        # -- APPLY UPDATE TO POLES --
        self.stab.K_z = self.stab.altitude_spec_update()

        if self.stab.delay_ratio_z < 0.09:
            self.ui.Warn_alarm.hide()
        elif self.stab.delay_ratio_z < 0.12:
            self.ui.Warn_alarm.setText("<font color='orange'>Warning: Approaching Instability")
            self.ui.Warn_alarm.show()
        else:
            self.ui.Warn_alarm.setText("<font color='red'>Alarm: Likely Instability")
            self.ui.Warn_alarm.show()

    def toggle_simulation(self):
        if self.quadcopter.DT_mode:
            return
        self.quadcopter.simulation_mode = not self.quadcopter.simulation_mode

        self.sim_1.x[:] = 0.0
        self.sim_2.x[:] = 0.0

        if self.quadcopter.simulation_mode:
            self.ui.sim_btn.setText("Simulation: ON")
            self.digital_twin.show()
            self.DT_front_marker.show()
            self.model.hide()
            self.front_marker.hide()
            self.ui.DT_btn.setDisabled(1)
        else:
            self.ui.sim_btn.setText("Simulation: OFF")
            self.model.show()
            self.front_marker.show()
            self.digital_twin.hide()
            self.DT_front_marker.hide()
            self.ui.DT_btn.setEnabled(1)

    def toggle_DT(self):
        if self.quadcopter.simulation_mode:
            return
        self.quadcopter.DT_mode = not self.quadcopter.DT_mode


        self.sim_2.x[3:8] = 0.0
        self.sim_2.x[8,0] = np.deg2rad(self.quadcopter.attitude.yaw)
        self.sim_2.x[0,0] = self.quadcopter.position.x
        self.sim_2.x[1,0] = self.quadcopter.position.y
        self.sim_2.x[2,0] = self.quadcopter.position.z

        if self.quadcopter.DT_mode:
            self.ui.model_select.setCurrentText("Linearised Model")
            self.ui.model_select.setDisabled(1)
            self.ui.DT_btn.setText("Digital Twin Mode: ON")
            self.digital_twin.show()
            self.DT_front_marker.show()
            self.model.show()
            self.front_marker.show()
            self.ui.sim_btn.setDisabled(1)
        else:
            self.ui.DT_btn.setText("Digital Twin Mode: OFF")
            self.ui.model_select.setEnabled(1)
            self.model.show()
            self.front_marker.show()
            self.digital_twin.hide()
            self.DT_front_marker.hide()
            self.ui.sim_btn.setEnabled(1)
    


    def update_pid_labels(self, kp, ki, kd):
        self.ui.P_label.setText(f"P: {kp:.2f}")
        self.ui.I_label.setText(f"I: {ki:.2f}")
        self.ui.D_label.setText(f"D: {kd:.2f}")

    def update_PP_labels(self, Tss, Mp):
        self.ui.P_label.setText(f"Settling time: {Tss:.2f} s")
        self.ui.I_label.setText(f"Overshoot: {Mp:.2f} %")
        self.ui.PP_k_label.setText(f"k_0 = {self.stab.K_z[0,0]:.2f}, k_1 = {self.stab.K_z[0,1]:.2f}, k_2 = {self.stab.K_z[0,2]:.2f}")

    def update_step_response(self):
        # elapsed = time.time() - self.step_start_time

        # self.response_time.append(elapsed)

        # if not self.quadcopter.simulation_mode:
        #     self.response_altitude.append(self.quadcopter.position.z)
        #     self.response_setpoint.append(self.quadcopter.controls.z)
        # elif self.ui.model_select.currentText().lower == "non-linear model":
        #     self.response_altitude.append(self.sim_non_linear.position.z)
        #     self.response_setpoint.append(self.sim_non_linear.controls.z)
        # elif self.ui.model_select.currentText().lower == "linearised model":
        #     self.response_altitude.append(self.sim_linear.position.z)
        #     self.response_setpoint.append(self.sim_linear.controls.z)

        # self.alt_curve.setData(
        #     list(self.response_time),
        #     list(self.response_altitude)
        # )

        # self.sp_curve.setData(
        #     list(self.response_time),
        #     list(self.response_setpoint)
        #     )
        return
    def reset_step_response(self):
        # self.response_time.clear()
        # self.response_altitude.clear()
        # self.response_setpoint.clear()
        # self.logging_response = True
        return

    def stop_step_response(self):
        self.logging_response = False

    def calibration_window(self):
        self.cal = CalibrationWindow(self.obs)
        self.cal.exec()
