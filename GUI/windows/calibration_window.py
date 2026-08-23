# Written by Jonah Habel 2026
# Flinders University
#
# calibrate_window.py
# -- used to instantiate and control imported calibration window UI from the designer --

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTimer, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QWidget)

from GUI.ui.ui_calibration import Ui_Dialog
from functions import append_settings

class CalibrationWindow(QDialog):
    def __init__(self, obs):
        self.quad = obs.quad
        self.obs = obs
        # instantiate calibrate window
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.defaults_append = {}
        self.timer = QTimer(self)
        self.timer_v = QTimer(self)
        self.timer.timeout.connect(self.test_acc)
        self.current_thrust = 10000.0
        self.acc_z_filtered = 0.995
        self.liftoff_count = 0

        # connect button clicks
        self.ui.calibrate_button.clicked.connect(self.calibrate_thrust)
        self.ui.close_button.clicked.connect(self.close)
        self.ui.save_button.clicked.connect(self.save_hover_thrust)

        # hide labels by default
        self.ui.label_2.hide()
        self.ui.label_3.hide()
        self.ui.label_4.hide()

    def save_hover_thrust(self):
        append_settings("init_defaults.txt", self.defaults_append)

    def calibrate_thrust(self):
        # step through thrust controls to find one that achieves hover acceleration
        self.ui.label_2.show()
        self.ui.label_3.show()
        self.acc_z_filtered = 0.995
        self.ui.calibrate_button.setText("Cancel Test")
        self.ui.calibrate_button.clicked.connect(self.cancel_thrust)
        self.testing = True
        self.timer.start(30)

    def test_acc(self):
        self.acc_z_filtered = 0.85 * self.acc_z_filtered + 0.15 * self.quad.acc_z
        print(self.acc_z_filtered)
        if not self.testing:
            return
        self.quad.controls.thrust = self.current_thrust
        self.ui.label_3.setText(f"PWM Thrust: {self.current_thrust:.0f}")
        if self.acc_z_filtered >= 1.01:
            self.liftoff_count += 1
        else:
            self.liftoff_count = 0
        if self.liftoff_count >= 3:
            self.defaults_append["hover thrust"] = self.quad.controls.thrust
            self.ui.label_2.hide()
            self.ui.label_3.hide()
            self.ui.label_4.show()
            self.ui.label_4.setText(f"Hover achieved! Hover thrust = {self.quad.controls.thrust:.0f}")
            self.ui.calibrate_button.setText("Calibrate Hover Thrust")
            self.ui.calibrate_button.clicked.connect(self.calibrate_thrust)
            self.quad.controls.thrust = 0
            self.liftoff_count = 0
            self.timer.stop()
            self.testing = False
        self.current_thrust += 100

    def cancel_thrust(self):
        self.testing = False
        self.ui.calibrate_button.setText("Calibrate Hover Thrust")
        self.ui.calibrate_button.clicked.connect(self.calibrate_thrust)
        self.quad.controls.thrust = 0.0
        self.current_thrust = 10000.0
        self.liftoff_count = 0
        self.ui.label_2.hide()
        self.ui.label_3.hide()
        self.ui.label_4.hide()
        self.timer.stop()

