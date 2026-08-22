# Written by Jonah Habel 2026
# Flinders University
#
# with assistance from Microsoft Copilot
# setup_window.py
# -- used to instantiate and control imported setup window UI from the designer --

from PySide6.QtWidgets import QDialog, QApplication
from GUI.ui.ui_setup import Ui_Dialog

from Classes.quadcopter import Quadcopter
from GUI.windows.calibration_window import CalibrationWindow
import functions, sys


class SetupWindow(QDialog):
    def __init__(
        self,
        defaults,
        comms_options,
        controlsystem_options,
        estimator_options
    ):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.quad = None

        self.values = {}

        self.cal = CalibrationWindow(self)

        # Populate controls
        self.ui.comms_dropdown.addItems(comms_options)
        self.ui.controlsystem_dropdown.addItems(controlsystem_options)
        self.ui.estimator_dropdown.addItems(estimator_options)

        # Set defaults
        self.ui.mass_input.setText(defaults.get("MASS", ""))

        if defaults.get("comms") in comms_options:
            self.ui.comms_dropdown.setCurrentText(
                defaults.get("comms")
            )

        if defaults.get("control system") in controlsystem_options:
            self.ui.controlsystem_dropdown.setCurrentText(
                defaults.get("control system")
            )

        if defaults.get("state estimator") in estimator_options:
            self.ui.estimator_dropdown.setCurrentText(
                defaults.get("state estimator")
            )

        # Signals
        self.ui.save_button.clicked.connect(self.save_defaults)

        self.ui.enter_button.clicked.connect(self.enter_pressed)

    def save_defaults(self):
        self.values["MASS"] = float(self.ui.mass_input.text())
        self.values["comms"] = self.ui.comms_dropdown.currentText()
        self.values["control system"] = self.ui.controlsystem_dropdown.currentText()
        self.values["state estimator"] = self.ui.estimator_dropdown.currentText()

        functions.save_settings(
            "init_defaults.txt",
            self.values
        )

    def enter_pressed(self):
        self.quad = Quadcopter(
            MASS=float(self.ui.mass_input.text()),
            comms=self.ui.comms_dropdown.currentText(),
            controller=None,
            estimator=self.ui.estimator_dropdown.currentText(),
            control_system=self.ui.controlsystem_dropdown.currentText()
        )

        self.accept()

# this will run the setup window before the main client, system will exit if this is cancelled
def run_setup():
    comms_options = ["Crazyradio"]
    controlsystem_options = ["PID", "Pole-placement"]
    estimator_options = ["Kalman Filter"]

    defaults = functions.load_settings("init_defaults.txt")

    window = SetupWindow(
        defaults,
        comms_options,
        controlsystem_options,
        estimator_options
    )

    if window.exec():
        return window.quad
    else:
        return None