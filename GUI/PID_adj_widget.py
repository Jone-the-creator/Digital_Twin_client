from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox
)


class PIDControlPanel(QWidget):
    gain_changed = pyqtSignal(str, str, float)
    # controller, gain_name, delta
    # e.g. ("altitude", "P", 0.05)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("PID Tuning")
        layout.addWidget(title)

        self.controller_select = QComboBox()
        self.controller_select.addItems(["Altitude", "Attitude"])
        layout.addWidget(self.controller_select)

        self.gain_labels = {}

        for gain in ["P", "I", "D"]:
            gain_layout = QVBoxLayout()

            self.gain_labels[gain] = QLabel(f"{gain}: 0.00")
            gain_layout.addWidget(self.gain_labels[gain])

            btn_row = QHBoxLayout()

            for delta in [-0.25, -0.05, 0.05, 0.25]:
                btn = QPushButton(f"{delta:+.2f}")
                btn.clicked.connect(
                    lambda checked=False, g=gain, d=delta:
                    self.change_gain(g, d)
                )
                btn_row.addWidget(btn)

            gain_layout.addLayout(btn_row)
            layout.addLayout(gain_layout)

        layout.addStretch()

    def change_gain(self, gain, delta):
        controller = self.controller_select.currentText().lower()
        self.gain_changed.emit(controller, gain, delta)

    def update_values(self, p, i, d):
        self.gain_labels["P"].setText(f"P: {p:.2f}")
        self.gain_labels["I"].setText(f"I: {i:.2f}")
        self.gain_labels["D"].setText(f"D: {d:.2f}")
