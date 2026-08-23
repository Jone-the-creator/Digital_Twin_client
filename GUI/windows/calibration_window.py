# Written by Jonah Habel 2026
# Flinders University
#
# calibrate_window.py
# -- used to instantiate and control imported calibration window UI from the designer --

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QWidget)

from GUI.ui.ui_calibration import Ui_Dialog

class CalibrationWindow(QDialog):
    def __init__(self, quad):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.calibrate_button.clicked.connect(self.hover_thrust)

    def hover_thrust(self):
        self.defaults["test"] = "test test"
