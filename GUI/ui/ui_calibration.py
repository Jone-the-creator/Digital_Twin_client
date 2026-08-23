# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calibrationtNxQnr.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(405, 150)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(130, 0, 151, 31))
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 181, 16))
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 70, 391, 16))
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 100, 381, 16))
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 120, 401, 29))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.close_button = QPushButton(self.widget)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.close_button)

        self.save_button = QPushButton(self.widget)
        self.save_button.setObjectName(u"save_button")
        font1 = QFont()
        font1.setPointSize(10)
        self.save_button.setFont(font1)
        self.save_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.save_button)

        self.calibrate_button = QPushButton(self.widget)
        self.calibrate_button.setObjectName(u"calibrate_button")

        self.horizontalLayout.addWidget(self.calibrate_button)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u" Calibration Window", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Calibration Mode", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Slowly increasing thrust...", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"PWM Thrust:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Hover achieved! Hover thrust = ", None))
        self.close_button.setText(QCoreApplication.translate("Dialog", u"Close", None))
        self.save_button.setText(QCoreApplication.translate("Dialog", u"Save as Default", None))
        self.calibrate_button.setText(QCoreApplication.translate("Dialog", u"Calibrate Hover Thrust", None))
    # retranslateUi

