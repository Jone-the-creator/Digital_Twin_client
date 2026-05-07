from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6 import QtCore
import pyqtgraph.opengl as gl
import numpy as np
import math

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

        layout = QVBoxLayout(self)

        # add reading widgets here
        layout.addWidget(self.battery)

        layout.addStretch()

    def update(self, battery):
        # add update functionality to readings (adjust change in control loop)
        self.battery.set_value(battery)