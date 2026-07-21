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
        """
        self.m1 = ThrustBar("M1")
        self.m2 = ThrustBar("M2")
        self.m3 = ThrustBar("M3")
        self.m4 = ThrustBar("M4")
        """

        layout = QHBoxLayout(self)
        layout.addWidget(self.total)
        """
        layout.addWidget(self.m1)
        layout.addWidget(self.m2)
        layout.addWidget(self.m3)
        layout.addWidget(self.m4)
        """
        
    def update(self, thrust):
        self.total.set_value(thrust)
        """
        self.m1.set_value(m1)
        self.m2.set_value(m2)
        self.m3.set_value(m3)
        self.m4.set_value(m4)
        """

class Reading(QWidget):
    def __init__(self, name = "Reading", hasProgressBar = False):
        super().__init__()

        self.name = name
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

    def set_value(self, value, suffix = ""): # If progress bar already set, suffix will automatically be %
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
            self.label.setText(f"{self.name}: {value} {suffix}")

class ReadingPanel(QWidget):
    def __init__(self):
        super().__init__()
        # instantiate readings here
        self.battery = Reading(name = "Battery", hasProgressBar= True)
        self.battvolt = Reading(name = "Battery Voltage")
        self.yaw = Reading(name = "Yaw")
        self.pitch = Reading(name = "Pitch")
        self.roll = Reading(name = "Roll")
        self.altitude = Reading(name = "Current Altitude")
        self.target_altitude = Reading(name = "Target Altitude")
        self.loop_rate = Reading(name = "Loop Rate")

        layout = QVBoxLayout(self)

        # add reading widgets here
        layout.addWidget(self.battery)
        layout.addWidget(self.battvolt)
        layout.addWidget(self.yaw)
        layout.addWidget(self.pitch)
        layout.addWidget(self.roll)
        layout.addWidget(self.altitude)
        layout.addWidget(self.target_altitude)
        layout.addWidget(self.loop_rate)

        layout.addStretch()

    def update(self, battery, battvolt, yaw, pitch, roll, altitude, target_altitude, loop_rate):
        # add update functionality to readings (adjust change in viewer.py)
        self.battery.set_value(battery)
        self.battvolt.set_value(battvolt)
        self.yaw.set_value(round(yaw, 2))
        self.pitch.set_value(round(pitch, 2))
        self.roll.set_value(round(roll, 2))
        self.altitude.set_value(round(altitude, 2))
        self.target_altitude.set_value(round(target_altitude, 2))
        self.loop_rate.set_value(round(loop_rate, 1))

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
        controller = self.controller_select.currentText().lower()
        self.gain_changed.emit(controller, gain, delta)

    def update_values(self, p, i, d):
        self.gain_labels["P"].setText(f"P: {p:.2f}")
        self.gain_labels["I"].setText(f"I: {i:.2f}")
        self.gain_labels["D"].setText(f"D: {d:.2f}")
