# Written by Jonah Habel 2026
# Flinders University
#
# calibrate_window.py
# -- used to instantiate and control imported calibration window UI from the designer --

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog

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

        # prepare variables, objects and dictionaries
        self.defaults_append = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.test_acc)
        self.current_thrust = 10000.0
        self.acc_z_filtered = 0.995 # start accelerometer filter biased under 1.0
        self.running_average = 0.0
        self.average_total = 0.0
        self.average_num = 0
        self.liftoff_count = 0

        # connect button clicks
        self.ui.calibrate_button.clicked.connect(self.calibrate_thrust)
        self.ui.close_button.clicked.connect(self.close)
        self.ui.save_button.clicked.connect(lambda: append_settings("init_defaults.txt", self.defaults_append))

        # hide labels by default
        self.ui.label_2.hide()
        self.ui.label_3.hide()
        self.ui.label_4.hide()

    # step through thrust controls to find one that achieves hover acceleration
    def calibrate_thrust(self):
        #show process labels
        self.ui.label_2.show()
        self.ui.label_3.show()

        # start accelerometer filter biased under 1.0
        self.acc_z_filtered = 0.995

        # change button to cancel button
        self.ui.calibrate_button.setText("Cancel Test")
        self.ui.calibrate_button.clicked.connect(self.cancel_thrust)

        # when completing subsequent tests, start closer to the average
        self.current_thrust = 0.8 * self.running_average

        self.testing = True
        self.timer.start(30)

    def test_acc(self):
        # lowpass filter the accelerometer reading (in Gs)
        self.acc_z_filtered = 0.85 * self.acc_z_filtered + 0.15 * self.quad.acc_z
        print(self.acc_z_filtered)

        # do not run if testing has been cancelled or finished
        if not self.testing:
            return
        self.quad.controls.thrust = self.current_thrust
        self.ui.label_3.setText(f"PWM Thrust: {self.current_thrust:.0f}")

        # check if the threshold has been reached 3 times in a row (90ms)
        if self.acc_z_filtered >= 1.01:
            self.liftoff_count += 1
        else:
            self.liftoff_count = 0
        if self.liftoff_count >= 3:
            # load into running average
            self.average_num += 1
            self.average_total += self.current_thrust
            self.running_average = self.average_total/self.average_num

            self.defaults_append["hover thrust"] = self.running_average

            # hide process labels and show hover thrust label
            self.ui.label_2.hide()
            self.ui.label_3.hide()
            self.ui.label_4.show()
            self.ui.label_4.setText(f"Hover achieved! Average hover thrust = {self.quad.controls.thrust:.0f} ({self.average_num} tests)")

            # reset the button
            self.ui.calibrate_button.setText("Calibrate Hover Thrust")
            self.ui.calibrate_button.clicked.connect(self.calibrate_thrust)

            # reset variables
            self.quad.controls.thrust = 0
            self.liftoff_count = 0
            self.timer.stop()
            self.testing = False

        # increase by 100 each loop (30ms)
        self.current_thrust += 100

    def cancel_thrust(self):
        # reset variables
        self.testing = False
        self.quad.controls.thrust = 0.0
        self.current_thrust = 0.0
        self.liftoff_count = 0

        # reset the button
        self.ui.calibrate_button.setText("Calibrate Hover Thrust")
        self.ui.calibrate_button.clicked.connect(self.calibrate_thrust)

        # hide all labels
        self.ui.label_2.hide()
        self.ui.label_3.hide()
        self.ui.label_4.hide()

        # stop timer
        self.timer.stop()

