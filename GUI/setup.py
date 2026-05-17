# setup.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
)

from Classes import Quadcopter, PS5Controller
import functions


class SetupWindow(QDialog):
    def __init__(self, defaults, comms_options, controlsystem_options, estimator_options):
        super().__init__()

        self.setWindowTitle("Quadcopter GUI")
        self.setFixedWidth(400)

        self.quad = None

        # --- Widgets ---
        self.id_input = QLineEdit(defaults.get("ID", ""))

        self.comms_dropdown = QComboBox()
        self.comms_dropdown.addItems(comms_options)
        
        self.controlsystem_dropdown = QComboBox()
        self.controlsystem_dropdown.addItems(controlsystem_options)

        self.estimator_dropdown = QComboBox()
        self.estimator_dropdown.addItems(estimator_options)

        if defaults.get("comms") in comms_options:
            self.comms_dropdown.setCurrentText(defaults.get("comms"))

        self.save_button = QPushButton("Save as defaults")
        self.enter_button = QPushButton("Enter")

        # --- Layout ---
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter your quadcopter ID:"))
        layout.addWidget(self.id_input)

        layout.addWidget(QLabel("Select supported communications system:"))
        layout.addWidget(self.comms_dropdown)

        layout.addWidget(QLabel("Select control system:"))
        layout.addWidget(self.controlsystem_dropdown)

        layout.addWidget(QLabel("Select state estimator:"))
        layout.addWidget(self.estimator_dropdown)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.save_button)
        btn_row.addWidget(self.enter_button)

        layout.addLayout(btn_row)

        self.setLayout(layout)

        # --- Signals ---
        self.save_button.clicked.connect(self.save_defaults)
        self.enter_button.clicked.connect(self.enter_pressed)

    # --- Actions ---
    def save_defaults(self):
        values = {
            "ID": self.id_input.text().strip(),
            "comms": self.comms_dropdown.currentText(),
            "control system": self.controlsystem_dropdown.currentText(),
            "state estimator": self.estimator_dropdown.currentText()
        }
        functions.save_settings("init_defaults.txt", values)
        print("Defaults saved:", values)

    def enter_pressed(self):
        self.quad = Quadcopter(
            ID=self.id_input.text().strip(),
            comms=self.comms_dropdown.currentText(),
            controller=None,
            estimator=self.estimator_dropdown.currentText(),
            control_system=self.controlsystem_dropdown.currentText()
        )

        print(f"{self.quad.comms} was selected for {self.quad.ID}")
        print(f"will be controlled with {self.quad.control_system}, observed using {self.quad.estimator}")
        self.accept()

# this will run the setup window before the main client, system will exit if this is cancelled
def run_setup():
    comms_options = ["Crazyradio"]
    controlsystem_options = ["PID"]
    estimator_options = ["Kalman Filter", "TEST"]

    defaults = functions.load_settings("init_defaults.txt")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

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