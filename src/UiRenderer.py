from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import logging

from src.UiActions import UiActions


class UiRenderer(QWidget):
    ui_actions = None

    def setupUi(self, MainWindow):
        self.ui_actions = UiActions(self)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1304, 977)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.mediaLabel = QtWidgets.QLabel(self.centralwidget)
        self.mediaLabel.setGeometry(QtCore.QRect(90, 10, 1111, 671))
        self.mediaLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.mediaLabel.setObjectName("mediaLabel")
        self.mediaLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.mediaFileLabel = QtWidgets.QLabel(self.centralwidget)
        self.mediaFileLabel.setGeometry(QtCore.QRect(1070, 690, 131, 31))
        self.mediaFileLabel.setAutoFillBackground(False)
        self.mediaFileLabel.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.mediaFileLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mediaFileLabel.setWordWrap(False)
        self.mediaFileLabel.setObjectName("mediaFileLabel")

        self.labelStringText = QtWidgets.QLabel(self.centralwidget)
        self.labelStringText.setGeometry(QtCore.QRect(970, 690, 91, 31))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setBold(True)
        font.setWeight(75)
        self.labelStringText.setFont(font)
        self.labelStringText.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStringText.setObjectName("labelStringText")

        self.availableLabelsTextLabel = QtWidgets.QLabel(self.centralwidget)
        self.availableLabelsTextLabel.setGeometry(QtCore.QRect(150, 700, 201, 21))
        font = QtGui.QFont()
        font.setFamily("Palatino Linotype")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.availableLabelsTextLabel.setFont(font)
        self.availableLabelsTextLabel.setAutoFillBackground(False)
        self.availableLabelsTextLabel.setScaledContents(False)
        self.availableLabelsTextLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.availableLabelsTextLabel.setObjectName("availableLabelsTextLabel")

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1304, 21))
        self.menubar.setObjectName("menubar")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.openFolder = QtWidgets.QAction(MainWindow)
        self.openFolder.setObjectName("openFolder")
        self.menuOpen.addAction(self.openFolder)
        self.menubar.addAction(self.menuOpen.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # open file action
        self.openFolder.triggered.connect(self.ui_actions.open_folder_dialog)
        self.menubar.addAction(self.openFolder)

        # update table widget with the labels
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(90, 730, 321, 192))
        self.tableWidget.setMinimumSize(QtCore.QSize(256, 192))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(("Name", "Shortcut", "Folder Path"))
        self.tableWidget.clicked.connect(self.ui_actions.update_label_entry)
        self.ui_actions.display_available_labels()

        logging.info("Rendered the UI")

        return self.ui_actions

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.labelStringText.setText(_translate("MainWindow", "Media Label"))
        self.menuOpen.setTitle(_translate("MainWindow", "Open"))
        self.openFolder.setText(_translate("MainWindow", "Folder"))
        self.availableLabelsTextLabel.setText(_translate("MainWindow", "Available Labels"))
