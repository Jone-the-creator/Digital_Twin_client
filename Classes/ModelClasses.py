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
        self.m1 = ThrustBar("M1")
        self.m2 = ThrustBar("M2")
        self.m3 = ThrustBar("M3")
        self.m4 = ThrustBar("M4")

        layout = QHBoxLayout(self)
        layout.addWidget(self.total)
        layout.addWidget(self.m1)
        layout.addWidget(self.m2)
        layout.addWidget(self.m3)
        layout.addWidget(self.m4)

    def update(self, thrust):
        self.total.set_value(thrust[0,0])
        self.m1.set_value(thrust[1,0])
        self.m2.set_value(thrust[2,0])
        self.m3.set_value(thrust[3,0])
        self.m4.set_value(thrust[4,0])
