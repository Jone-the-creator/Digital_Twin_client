# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowlSZapy.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QProgressBar, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.recording_label = QLabel(self.centralwidget)
        self.recording_label.setObjectName(u"recording_label")
        self.recording_label.setGeometry(QRect(920, 720, 67, 16))
        self.recording_label.setStyleSheet(u"color: rgb(255, 0, 0);\n"
"font: 700 9pt \"Segoe UI\";")
        self.gl_container = QWidget(self.centralwidget)
        self.gl_container.setObjectName(u"gl_container")
        self.gl_container.setGeometry(QRect(10, 50, 601, 691))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gl_container.sizePolicy().hasHeightForWidth())
        self.gl_container.setSizePolicy(sizePolicy)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(640, 40, 551, 16))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 20, 601, 26))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.battery_label = QLabel(self.widget)
        self.battery_label.setObjectName(u"battery_label")

        self.horizontalLayout.addWidget(self.battery_label)

        self.battery_bar = QProgressBar(self.widget)
        self.battery_bar.setObjectName(u"battery_bar")
        self.battery_bar.setAutoFillBackground(False)
        self.battery_bar.setValue(0)

        self.horizontalLayout.addWidget(self.battery_bar)

        self.widget1 = QWidget(self.centralwidget)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(990, 691, 204, 51))
        self.verticalLayout = QVBoxLayout(self.widget1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.sim_btn = QPushButton(self.widget1)
        self.sim_btn.setObjectName(u"sim_btn")

        self.verticalLayout.addWidget(self.sim_btn)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.start_recording_btn = QPushButton(self.widget1)
        self.start_recording_btn.setObjectName(u"start_recording_btn")

        self.horizontalLayout_2.addWidget(self.start_recording_btn)

        self.stop_recording_btn = QPushButton(self.widget1)
        self.stop_recording_btn.setObjectName(u"stop_recording_btn")

        self.horizontalLayout_2.addWidget(self.stop_recording_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.widget2 = QWidget(self.centralwidget)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setGeometry(QRect(630, 400, 561, 221))
        self.verticalLayout_2 = QVBoxLayout(self.widget2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel(self.widget2)
        self.title.setObjectName(u"title")

        self.verticalLayout_2.addWidget(self.title)

        self.controller_select = QComboBox(self.widget2)
        self.controller_select.setObjectName(u"controller_select")

        self.verticalLayout_2.addWidget(self.controller_select)

        self.P_label = QLabel(self.widget2)
        self.P_label.setObjectName(u"P_label")

        self.verticalLayout_2.addWidget(self.P_label)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.p_sub_large = QPushButton(self.widget2)
        self.p_sub_large.setObjectName(u"p_sub_large")

        self.horizontalLayout_3.addWidget(self.p_sub_large)

        self.p_sub_small = QPushButton(self.widget2)
        self.p_sub_small.setObjectName(u"p_sub_small")

        self.horizontalLayout_3.addWidget(self.p_sub_small)

        self.p_add_small = QPushButton(self.widget2)
        self.p_add_small.setObjectName(u"p_add_small")

        self.horizontalLayout_3.addWidget(self.p_add_small)

        self.p_add_large = QPushButton(self.widget2)
        self.p_add_large.setObjectName(u"p_add_large")

        self.horizontalLayout_3.addWidget(self.p_add_large)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.I_label = QLabel(self.widget2)
        self.I_label.setObjectName(u"I_label")

        self.verticalLayout_2.addWidget(self.I_label)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.i_sub_large = QPushButton(self.widget2)
        self.i_sub_large.setObjectName(u"i_sub_large")

        self.horizontalLayout_4.addWidget(self.i_sub_large)

        self.i_sub_small = QPushButton(self.widget2)
        self.i_sub_small.setObjectName(u"i_sub_small")

        self.horizontalLayout_4.addWidget(self.i_sub_small)

        self.i_add_small = QPushButton(self.widget2)
        self.i_add_small.setObjectName(u"i_add_small")

        self.horizontalLayout_4.addWidget(self.i_add_small)

        self.i_add_large = QPushButton(self.widget2)
        self.i_add_large.setObjectName(u"i_add_large")

        self.horizontalLayout_4.addWidget(self.i_add_large)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.D_label = QLabel(self.widget2)
        self.D_label.setObjectName(u"D_label")

        self.verticalLayout_2.addWidget(self.D_label)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.d_sub_large = QPushButton(self.widget2)
        self.d_sub_large.setObjectName(u"d_sub_large")

        self.horizontalLayout_5.addWidget(self.d_sub_large)

        self.d_sub_small = QPushButton(self.widget2)
        self.d_sub_small.setObjectName(u"d_sub_small")

        self.horizontalLayout_5.addWidget(self.d_sub_small)

        self.d_add_small = QPushButton(self.widget2)
        self.d_add_small.setObjectName(u"d_add_small")

        self.horizontalLayout_5.addWidget(self.d_add_small)

        self.d_add_large = QPushButton(self.widget2)
        self.d_add_large.setObjectName(u"d_add_large")

        self.horizontalLayout_5.addWidget(self.d_add_large)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.widget3 = QWidget(self.centralwidget)
        self.widget3.setObjectName(u"widget3")
        self.widget3.setGeometry(QRect(630, 60, 561, 171))
        self.verticalLayout_3 = QVBoxLayout(self.widget3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.yaw_reading = QLabel(self.widget3)
        self.yaw_reading.setObjectName(u"yaw_reading")

        self.verticalLayout_3.addWidget(self.yaw_reading)

        self.pitch_reading = QLabel(self.widget3)
        self.pitch_reading.setObjectName(u"pitch_reading")

        self.verticalLayout_3.addWidget(self.pitch_reading)

        self.roll_reading = QLabel(self.widget3)
        self.roll_reading.setObjectName(u"roll_reading")

        self.verticalLayout_3.addWidget(self.roll_reading)

        self.altitude_reading = QLabel(self.widget3)
        self.altitude_reading.setObjectName(u"altitude_reading")

        self.verticalLayout_3.addWidget(self.altitude_reading)

        self.altitude_sp_reading = QLabel(self.widget3)
        self.altitude_sp_reading.setObjectName(u"altitude_sp_reading")

        self.verticalLayout_3.addWidget(self.altitude_sp_reading)

        self.loop_rate_reading = QLabel(self.widget3)
        self.loop_rate_reading.setObjectName(u"loop_rate_reading")

        self.verticalLayout_3.addWidget(self.loop_rate_reading)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.recording_label.setText(QCoreApplication.translate("MainWindow", u"\u25cf Recording", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Live Readings", None))
        self.battery_label.setText(QCoreApplication.translate("MainWindow", u"Battery:", None))
        self.sim_btn.setText(QCoreApplication.translate("MainWindow", u"Simulation: OFF", None))
        self.start_recording_btn.setText(QCoreApplication.translate("MainWindow", u"Start Recording", None))
        self.stop_recording_btn.setText(QCoreApplication.translate("MainWindow", u"Stop Recording", None))
        self.title.setText(QCoreApplication.translate("MainWindow", u"PID Tuning", None))
        self.P_label.setText(QCoreApplication.translate("MainWindow", u"P:", None))
        self.p_sub_large.setText(QCoreApplication.translate("MainWindow", u"-0.25", None))
        self.p_sub_small.setText(QCoreApplication.translate("MainWindow", u"-0.05", None))
        self.p_add_small.setText(QCoreApplication.translate("MainWindow", u"+0.05", None))
        self.p_add_large.setText(QCoreApplication.translate("MainWindow", u"+0.25", None))
        self.I_label.setText(QCoreApplication.translate("MainWindow", u"I:", None))
        self.i_sub_large.setText(QCoreApplication.translate("MainWindow", u"-0.25", None))
        self.i_sub_small.setText(QCoreApplication.translate("MainWindow", u"-0.05", None))
        self.i_add_small.setText(QCoreApplication.translate("MainWindow", u"+0.05", None))
        self.i_add_large.setText(QCoreApplication.translate("MainWindow", u"+0.25", None))
        self.D_label.setText(QCoreApplication.translate("MainWindow", u"D:", None))
        self.d_sub_large.setText(QCoreApplication.translate("MainWindow", u"-0.25", None))
        self.d_sub_small.setText(QCoreApplication.translate("MainWindow", u"-0.05", None))
        self.d_add_small.setText(QCoreApplication.translate("MainWindow", u"+0.05", None))
        self.d_add_large.setText(QCoreApplication.translate("MainWindow", u"+0.25", None))
        self.yaw_reading.setText(QCoreApplication.translate("MainWindow", u"Yaw: ", None))
        self.pitch_reading.setText(QCoreApplication.translate("MainWindow", u"Pitch:", None))
        self.roll_reading.setText(QCoreApplication.translate("MainWindow", u"Roll:", None))
        self.altitude_reading.setText(QCoreApplication.translate("MainWindow", u"Current Altitude:", None))
        self.altitude_sp_reading.setText(QCoreApplication.translate("MainWindow", u"Altitude Setpoint:", None))
        self.loop_rate_reading.setText(QCoreApplication.translate("MainWindow", u"Loop Rate:", None))
    # retranslateUi

