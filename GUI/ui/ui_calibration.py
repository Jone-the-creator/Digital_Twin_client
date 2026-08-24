# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calibrationvopsBF.ui'
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
        self.title = QLabel(Dialog)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(130, 0, 151, 31))
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setUnderline(True)
        self.title.setFont(font)
        self.status = QLabel(Dialog)
        self.status.setObjectName(u"status")
        self.status.setGeometry(QRect(10, 40, 181, 16))
        self.result_1 = QLabel(Dialog)
        self.result_1.setObjectName(u"result_1")
        self.result_1.setGeometry(QRect(10, 70, 391, 16))
        self.result_2 = QLabel(Dialog)
        self.result_2.setObjectName(u"result_2")
        self.result_2.setGeometry(QRect(10, 100, 381, 16))
        self.layoutWidget = QWidget(Dialog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 120, 401, 29))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.close_button = QPushButton(self.layoutWidget)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.close_button)

        self.save_button = QPushButton(self.layoutWidget)
        self.save_button.setObjectName(u"save_button")
        font1 = QFont()
        font1.setPointSize(10)
        self.save_button.setFont(font1)
        self.save_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.save_button)

        self.calibrate_button = QPushButton(self.layoutWidget)
        self.calibrate_button.setObjectName(u"calibrate_button")

        self.horizontalLayout.addWidget(self.calibrate_button)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u" Calibration Window", None))
        self.title.setText(QCoreApplication.translate("Dialog", u"Calibration Mode", None))
        self.status.setText(QCoreApplication.translate("Dialog", u"Slowly increasing thrust...", None))
        self.result_1.setText(QCoreApplication.translate("Dialog", u"PWM Thrust:", None))
        self.result_2.setText(QCoreApplication.translate("Dialog", u"Hover achieved! Hover thrust = ", None))
        self.close_button.setText(QCoreApplication.translate("Dialog", u"Close", None))
        self.save_button.setText(QCoreApplication.translate("Dialog", u"Save as Default", None))
        self.calibrate_button.setText(QCoreApplication.translate("Dialog", u"Calibrate Hover Thrust", None))
    # retranslateUi

