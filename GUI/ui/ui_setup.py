# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setup_dialogAAGJnP.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(481, 332)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 6, 459, 311))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mass_label = QLabel(self.widget)
        self.mass_label.setObjectName(u"mass_label")
        font = QFont()
        font.setPointSize(10)
        self.mass_label.setFont(font)

        self.verticalLayout.addWidget(self.mass_label)

        self.mass_input = QLineEdit(self.widget)
        self.mass_input.setObjectName(u"mass_input")

        self.verticalLayout.addWidget(self.mass_input)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.linear_drag_lbl = QLabel(self.widget)
        self.linear_drag_lbl.setObjectName(u"linear_drag_lbl")
        self.linear_drag_lbl.setFont(font)

        self.gridLayout.addWidget(self.linear_drag_lbl, 0, 0, 1, 1)

        self.non_linear_drag_lbl = QLabel(self.widget)
        self.non_linear_drag_lbl.setObjectName(u"non_linear_drag_lbl")
        self.non_linear_drag_lbl.setFont(font)

        self.gridLayout.addWidget(self.non_linear_drag_lbl, 0, 1, 1, 1)

        self.linear_drag_in = QLineEdit(self.widget)
        self.linear_drag_in.setObjectName(u"linear_drag_in")

        self.gridLayout.addWidget(self.linear_drag_in, 1, 0, 1, 1)

        self.non_linear_drag_in = QLineEdit(self.widget)
        self.non_linear_drag_in.setObjectName(u"non_linear_drag_in")

        self.gridLayout.addWidget(self.non_linear_drag_in, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.comm_label = QLabel(self.widget)
        self.comm_label.setObjectName(u"comm_label")
        self.comm_label.setFont(font)

        self.verticalLayout.addWidget(self.comm_label)

        self.comms_dropdown = QComboBox(self.widget)
        self.comms_dropdown.setObjectName(u"comms_dropdown")
        self.comms_dropdown.setFont(font)

        self.verticalLayout.addWidget(self.comms_dropdown)

        self.controller_label = QLabel(self.widget)
        self.controller_label.setObjectName(u"controller_label")
        self.controller_label.setFont(font)

        self.verticalLayout.addWidget(self.controller_label)

        self.controlsystem_dropdown = QComboBox(self.widget)
        self.controlsystem_dropdown.setObjectName(u"controlsystem_dropdown")
        self.controlsystem_dropdown.setFont(font)

        self.verticalLayout.addWidget(self.controlsystem_dropdown)

        self.estimator_label = QLabel(self.widget)
        self.estimator_label.setObjectName(u"estimator_label")
        self.estimator_label.setFont(font)

        self.verticalLayout.addWidget(self.estimator_label)

        self.estimator_dropdown = QComboBox(self.widget)
        self.estimator_dropdown.setObjectName(u"estimator_dropdown")
        self.estimator_dropdown.setFont(font)

        self.verticalLayout.addWidget(self.estimator_dropdown)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.save_button = QPushButton(self.widget)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setFont(font)
        self.save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout.addWidget(self.save_button)

        self.enter_button = QPushButton(self.widget)
        self.enter_button.setObjectName(u"enter_button")
        self.enter_button.setFont(font)
        self.enter_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout.addWidget(self.enter_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        self.enter_button.setDefault(True)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Digital Twin Setup Window", None))
        self.mass_label.setText(QCoreApplication.translate("Dialog", u"Enter your quadcopter's mass (kg):", None))
        self.linear_drag_lbl.setText(QCoreApplication.translate("Dialog", u"Enter linear aerodynamic coefficient:", None))
        self.non_linear_drag_lbl.setText(QCoreApplication.translate("Dialog", u"Enter non-linear aerodynamic coefficient:", None))
        self.comm_label.setText(QCoreApplication.translate("Dialog", u"Select supported communication system:", None))
        self.controller_label.setText(QCoreApplication.translate("Dialog", u"Select control system:", None))
        self.estimator_label.setText(QCoreApplication.translate("Dialog", u"Select state estimator:", None))
        self.save_button.setText(QCoreApplication.translate("Dialog", u"Save as defaults", None))
        self.enter_button.setText(QCoreApplication.translate("Dialog", u"Enter", None))
    # retranslateUi

