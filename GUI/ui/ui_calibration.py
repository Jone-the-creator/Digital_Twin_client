# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calibrationDTupyq.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QWidget)

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
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(0, 120, 81, 26))
        self.pushButton_2 = QPushButton(Dialog)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(250, 120, 151, 26))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 181, 16))
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 70, 121, 16))
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 100, 261, 16))
        self.pushButton_3 = QPushButton(Dialog)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(90, 120, 151, 26))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Calibration Mode", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Close", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"Calibrate Hover Thrust", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Slowly increasing thrust...", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"PWM Thrust:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Hover achieved! Hover thrust = ", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog", u"Save Hover Thrust", None))
    # retranslateUi

