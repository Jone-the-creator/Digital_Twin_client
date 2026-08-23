# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowWITeQe.ui'
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
        self.Readings_title = QLabel(self.centralwidget)
        self.Readings_title.setObjectName(u"Readings_title")
        self.Readings_title.setGeometry(QRect(640, 40, 201, 16))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setUnderline(True)
        self.Readings_title.setFont(font)
        self.Readings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 20, 601, 26))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.battery_label = QLabel(self.layoutWidget)
        self.battery_label.setObjectName(u"battery_label")

        self.horizontalLayout.addWidget(self.battery_label)

        self.battery_bar = QProgressBar(self.layoutWidget)
        self.battery_bar.setObjectName(u"battery_bar")
        self.battery_bar.setAutoFillBackground(False)
        self.battery_bar.setValue(0)

        self.horizontalLayout.addWidget(self.battery_bar)

        self.layoutWidget1 = QWidget(self.centralwidget)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(990, 691, 204, 62))
        self.verticalLayout = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.sim_btn = QPushButton(self.layoutWidget1)
        self.sim_btn.setObjectName(u"sim_btn")

        self.verticalLayout.addWidget(self.sim_btn)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.start_recording_btn = QPushButton(self.layoutWidget1)
        self.start_recording_btn.setObjectName(u"start_recording_btn")

        self.horizontalLayout_2.addWidget(self.start_recording_btn)

        self.stop_recording_btn = QPushButton(self.layoutWidget1)
        self.stop_recording_btn.setObjectName(u"stop_recording_btn")

        self.horizontalLayout_2.addWidget(self.stop_recording_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.layoutWidget2 = QWidget(self.centralwidget)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(630, 60, 211, 171))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.yaw_reading = QLabel(self.layoutWidget2)
        self.yaw_reading.setObjectName(u"yaw_reading")

        self.verticalLayout_3.addWidget(self.yaw_reading)

        self.pitch_reading = QLabel(self.layoutWidget2)
        self.pitch_reading.setObjectName(u"pitch_reading")

        self.verticalLayout_3.addWidget(self.pitch_reading)

        self.roll_reading = QLabel(self.layoutWidget2)
        self.roll_reading.setObjectName(u"roll_reading")

        self.verticalLayout_3.addWidget(self.roll_reading)

        self.altitude_reading = QLabel(self.layoutWidget2)
        self.altitude_reading.setObjectName(u"altitude_reading")

        self.verticalLayout_3.addWidget(self.altitude_reading)

        self.altitude_sp_reading = QLabel(self.layoutWidget2)
        self.altitude_sp_reading.setObjectName(u"altitude_sp_reading")

        self.verticalLayout_3.addWidget(self.altitude_sp_reading)

        self.loop_rate_reading = QLabel(self.layoutWidget2)
        self.loop_rate_reading.setObjectName(u"loop_rate_reading")

        self.verticalLayout_3.addWidget(self.loop_rate_reading)

        self.Response_title = QLabel(self.centralwidget)
        self.Response_title.setObjectName(u"Response_title")
        self.Response_title.setGeometry(QRect(930, 40, 201, 16))
        self.Response_title.setFont(font)
        self.Response_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(860, 60, 331, 281))
        self.layoutWidget3 = QWidget(self.centralwidget)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(630, 400, 561, 266))
        self.verticalLayout_5 = QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.title = QLabel(self.layoutWidget3)
        self.title.setObjectName(u"title")

        self.verticalLayout_2.addWidget(self.title)

        self.controller_select = QComboBox(self.layoutWidget3)
        self.controller_select.setObjectName(u"controller_select")

        self.verticalLayout_2.addWidget(self.controller_select)

        self.P_label = QLabel(self.layoutWidget3)
        self.P_label.setObjectName(u"P_label")

        self.verticalLayout_2.addWidget(self.P_label)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.p_sub_large = QPushButton(self.layoutWidget3)
        self.p_sub_large.setObjectName(u"p_sub_large")

        self.horizontalLayout_3.addWidget(self.p_sub_large)

        self.p_sub_small = QPushButton(self.layoutWidget3)
        self.p_sub_small.setObjectName(u"p_sub_small")

        self.horizontalLayout_3.addWidget(self.p_sub_small)

        self.p_add_small = QPushButton(self.layoutWidget3)
        self.p_add_small.setObjectName(u"p_add_small")

        self.horizontalLayout_3.addWidget(self.p_add_small)

        self.p_add_large = QPushButton(self.layoutWidget3)
        self.p_add_large.setObjectName(u"p_add_large")

        self.horizontalLayout_3.addWidget(self.p_add_large)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.I_label = QLabel(self.layoutWidget3)
        self.I_label.setObjectName(u"I_label")

        self.verticalLayout_2.addWidget(self.I_label)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.i_sub_large = QPushButton(self.layoutWidget3)
        self.i_sub_large.setObjectName(u"i_sub_large")

        self.horizontalLayout_4.addWidget(self.i_sub_large)

        self.i_sub_small = QPushButton(self.layoutWidget3)
        self.i_sub_small.setObjectName(u"i_sub_small")

        self.horizontalLayout_4.addWidget(self.i_sub_small)

        self.i_add_small = QPushButton(self.layoutWidget3)
        self.i_add_small.setObjectName(u"i_add_small")

        self.horizontalLayout_4.addWidget(self.i_add_small)

        self.i_add_large = QPushButton(self.layoutWidget3)
        self.i_add_large.setObjectName(u"i_add_large")

        self.horizontalLayout_4.addWidget(self.i_add_large)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.D_label = QLabel(self.layoutWidget3)
        self.D_label.setObjectName(u"D_label")

        self.verticalLayout_2.addWidget(self.D_label)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.d_sub_large = QPushButton(self.layoutWidget3)
        self.d_sub_large.setObjectName(u"d_sub_large")

        self.horizontalLayout_5.addWidget(self.d_sub_large)

        self.d_sub_small = QPushButton(self.layoutWidget3)
        self.d_sub_small.setObjectName(u"d_sub_small")

        self.horizontalLayout_5.addWidget(self.d_sub_small)

        self.d_add_small = QPushButton(self.layoutWidget3)
        self.d_add_small.setObjectName(u"d_add_small")

        self.horizontalLayout_5.addWidget(self.d_add_small)

        self.d_add_large = QPushButton(self.layoutWidget3)
        self.d_add_large.setObjectName(u"d_add_large")

        self.horizontalLayout_5.addWidget(self.d_add_large)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.PP_k_label = QLabel(self.layoutWidget3)
        self.PP_k_label.setObjectName(u"PP_k_label")

        self.verticalLayout_4.addWidget(self.PP_k_label)


        self.verticalLayout_5.addLayout(self.verticalLayout_4)

        self.Warn_alarm = QLabel(self.layoutWidget3)
        self.Warn_alarm.setObjectName(u"Warn_alarm")
        font1 = QFont()
        font1.setBold(True)
        self.Warn_alarm.setFont(font1)
        self.Warn_alarm.setStyleSheet(u"color: rgb(255, 170, 0);")

        self.verticalLayout_5.addWidget(self.Warn_alarm)

        self.calibrate_button = QPushButton(self.centralwidget)
        self.calibrate_button.setObjectName(u"calibrate_button")
        self.calibrate_button.setGeometry(QRect(630, 720, 119, 27))
        font2 = QFont()
        font2.setPointSize(10)
        self.calibrate_button.setFont(font2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 33))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.recording_label.setText(QCoreApplication.translate("MainWindow", u"\u25cf Recording", None))
        self.Readings_title.setText(QCoreApplication.translate("MainWindow", u"Live Readings", None))
        self.battery_label.setText(QCoreApplication.translate("MainWindow", u"Battery:", None))
        self.sim_btn.setText(QCoreApplication.translate("MainWindow", u"Simulation: OFF", None))
        self.start_recording_btn.setText(QCoreApplication.translate("MainWindow", u"Start Recording", None))
        self.stop_recording_btn.setText(QCoreApplication.translate("MainWindow", u"Stop Recording", None))
        self.yaw_reading.setText(QCoreApplication.translate("MainWindow", u"Yaw: ", None))
        self.pitch_reading.setText(QCoreApplication.translate("MainWindow", u"Pitch:", None))
        self.roll_reading.setText(QCoreApplication.translate("MainWindow", u"Roll:", None))
        self.altitude_reading.setText(QCoreApplication.translate("MainWindow", u"Current Altitude:", None))
        self.altitude_sp_reading.setText(QCoreApplication.translate("MainWindow", u"Altitude Setpoint:", None))
        self.loop_rate_reading.setText(QCoreApplication.translate("MainWindow", u"Loop Rate:", None))
        self.Response_title.setText(QCoreApplication.translate("MainWindow", u"Step Response", None))
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
        self.PP_k_label.setText(QCoreApplication.translate("MainWindow", u"k_0 = ", None))
        self.Warn_alarm.setText(QCoreApplication.translate("MainWindow", u"Warning: Approaching instability", None))
        self.calibrate_button.setText(QCoreApplication.translate("MainWindow", u"Calibrate", None))
    # retranslateUi

