# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setup_dialogFBewZK.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(390, 278)
        self.layoutWidget = QWidget(Dialog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(12, 5, 371, 221))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mass_label = QLabel(self.layoutWidget)
        self.mass_label.setObjectName(u"mass_label")
        font = QFont()
        font.setPointSize(10)
        self.mass_label.setFont(font)

        self.verticalLayout.addWidget(self.mass_label)

        self.mass_input = QLineEdit(self.layoutWidget)
        self.mass_input.setObjectName(u"mass_input")

        self.verticalLayout.addWidget(self.mass_input)

        self.comm_label = QLabel(self.layoutWidget)
        self.comm_label.setObjectName(u"comm_label")
        self.comm_label.setFont(font)

        self.verticalLayout.addWidget(self.comm_label)

        self.comms_dropdown = QComboBox(self.layoutWidget)
        self.comms_dropdown.setObjectName(u"comms_dropdown")
        self.comms_dropdown.setFont(font)

        self.verticalLayout.addWidget(self.comms_dropdown)

        self.controller_label = QLabel(self.layoutWidget)
        self.controller_label.setObjectName(u"controller_label")
        self.controller_label.setFont(font)

        self.verticalLayout.addWidget(self.controller_label)

        self.controlsystem_dropdown = QComboBox(self.layoutWidget)
        self.controlsystem_dropdown.setObjectName(u"controlsystem_dropdown")
        self.controlsystem_dropdown.setFont(font)

        self.verticalLayout.addWidget(self.controlsystem_dropdown)

        self.estimator_label = QLabel(self.layoutWidget)
        self.estimator_label.setObjectName(u"estimator_label")
        self.estimator_label.setFont(font)

        self.verticalLayout.addWidget(self.estimator_label)

        self.estimator_dropdown = QComboBox(self.layoutWidget)
        self.estimator_dropdown.setObjectName(u"estimator_dropdown")
        self.estimator_dropdown.setFont(font)

        self.verticalLayout.addWidget(self.estimator_dropdown)

        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(11, 241, 371, 29))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.save_button = QPushButton(self.widget)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setFont(font)

        self.horizontalLayout.addWidget(self.save_button)

        self.enter_button = QPushButton(self.widget)
        self.enter_button.setObjectName(u"enter_button")
        self.enter_button.setFont(font)

        self.horizontalLayout.addWidget(self.enter_button)


        self.retranslateUi(Dialog)

        self.enter_button.setDefault(True)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Digital Twin Setup Window", None))
        self.mass_label.setText(QCoreApplication.translate("Dialog", u"Enter your quadcopter's mass (kg):", None))
        self.comm_label.setText(QCoreApplication.translate("Dialog", u"Select supported communication system:", None))
        self.controller_label.setText(QCoreApplication.translate("Dialog", u"Select control system:", None))
        self.estimator_label.setText(QCoreApplication.translate("Dialog", u"Select state estimator:", None))
        self.save_button.setText(QCoreApplication.translate("Dialog", u"Save as defaults", None))
        self.enter_button.setText(QCoreApplication.translate("Dialog", u"Enter", None))
    # retranslateUi

