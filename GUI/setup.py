# setup.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
)

from Classes import Quadcopter, PS5Controller
import functions


class SetupWindow(QDialog):
    def __init__(self, defaults, comms_options):
        super().__init__()

        self.setWindowTitle("Quadcopter GUI")
        self.setFixedWidth(400)

        self.quad = None

        # --- Widgets ---
        self.id_input = QLineEdit(defaults.get("ID", ""))

        self.comms_dropdown = QComboBox()
        self.comms_dropdown.addItems(comms_options)

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
            "comms": self.comms_dropdown.currentText().strip()
        }
        functions.save_settings("init_defaults.txt", values)
        print("Defaults saved:", values)

    def enter_pressed(self):
        self.quad = Quadcopter(
            ID=self.id_input.text().strip(),
            comms=self.comms_dropdown.currentText(),
            controller=None
        )

        print(f"{self.quad.comms} was selected for {self.quad.ID}")
        self.accept()

# this will run the setup window before the main client, system will exit if this is cancelled
def run_setup():
    comms_options = ["Crazyradio", "TEST"]

    defaults = functions.load_settings("init_defaults.txt")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    window = SetupWindow(
        defaults,
        comms_options,
    )

    if window.exec():
        return window.quad
    else:
        return None