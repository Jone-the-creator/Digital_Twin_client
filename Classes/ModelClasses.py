from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar
)


class ThrustBar(QWidget):
    def __init__(self, title):
        super().__init__()

        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bar = QProgressBar()
        self.bar.setOrientation(Qt.Orientation.Vertical)
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedSize(30, 160)

        self.percent = QLabel("0%")
        self.percent.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.bar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.percent)

    def set_value(self, percent):
        percent = max(0, min(100, int(percent)))
        self.bar.setValue(percent)
        self.percent.setText(f"{percent}%")


class ThrustPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.total = ThrustBar("Thrust")

        layout = QHBoxLayout(self)
        layout.addWidget(self.total)
        
    def update_thrust(self, thrust):
        self.total.set_value(thrust)

class Reading(QWidget):
    def __init__(self, name = "Reading", unit = "", hasProgressBar = False):
        super().__init__()

        self.name = name
        self.unit = unit
        self.hasProgressBar = hasProgressBar
        self.bar = None

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Label (text)
        self.label = QLabel(f"{self.name}: 0")
        layout.addWidget(self.label)
        
        if self.hasProgressBar:
            # Progress bar
            self.bar = QProgressBar()
            self.bar.setRange(0, 100)
            
            layout.addWidget(self.bar)

    def set_value(self, value): # If progress bar already set, suffix will automatically be %
        # Clamp value to 0–100
        if value is None:
            # Show placeholder instead of crashing
            self.label.setText(f"{self.name}: --")
            if self.bar:
                self.bar.setValue(0)
            return

        if self.hasProgressBar:
            value = max(0, min(100, value))
            self.bar.setValue(value)
            self.label.setText(f"{self.name}: {value}%")
            if value < 20:
                color = "red"
            elif value < 50:
                color = "orange"
            else:
                color = "green"
            self.bar.setStyleSheet(f"QProgressBar::chunk {{ background: {color}; }}")

        else:
            self.label.setText(f"{self.name}: {value} {self.unit}")

class ReadingPanel(QWidget):
    def __init__(self):
        super().__init__()
        # instantiate readings here
        self.readings = {
            "battery_percent": Reading("Battery", hasProgressBar=True),
            "yaw": Reading("Yaw", "°"),
            "pitch": Reading("Pitch", "°"),
            "roll": Reading("Roll", "°"),
            "altitude": Reading("Current Altitude", "m"),
            "altitude setpoint": Reading("Altitude Setpoint", "m"),
            "loop_rate": Reading("Loop Rate", "Hz")
        }

        layout = QVBoxLayout(self)

        # add reading widgets here
        for reading in self.readings.values():
            layout.addWidget(reading)

        layout.addStretch()

    def update_readings(self, data):
        for name, value in data.items():
            if name in self.readings:
                self.readings[name].set_value(value)

class PIDControlPanel(QWidget):
    gain_changed = pyqtSignal(str, float)
    # controller, gain_name, delta
    # e.g. ("altitude", "P", 0.05)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("PID Tuning")
        layout.addWidget(title)

        self.controller_select = QComboBox()
        self.controller_select.addItems(["Altitude Controller", "Attitude Controller"])
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
        self.gain_changed.emit(gain, delta)

    def update_values(self, p, i, d):
        self.gain_labels["P"].setText(f"P: {p:.2f}")
        self.gain_labels["I"].setText(f"I: {i:.2f}")
        self.gain_labels["D"].setText(f"D: {d:.2f}")
