# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'start_window.ui'
#
# Created: Mon Apr  6 20:52:07 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(398, 196)
        Dialog.setWindowTitle("")
        self.gridLayoutWidget = QtGui.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 381, 121))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.event_box = QtGui.QComboBox(self.gridLayoutWidget)
        self.event_box.setObjectName("event_box")
        self.gridLayout.addWidget(self.event_box, 2, 1, 1, 1)
        self.year_label = QtGui.QLabel(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.year_label.sizePolicy().hasHeightForWidth())
        self.year_label.setSizePolicy(sizePolicy)
        self.year_label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.year_label.setObjectName("year_label")
        self.gridLayout.addWidget(self.year_label, 1, 0, 1, 1)
        self.event_label = QtGui.QLabel(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.event_label.sizePolicy().hasHeightForWidth())
        self.event_label.setSizePolicy(sizePolicy)
        self.event_label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.event_label.setObjectName("event_label")
        self.gridLayout.addWidget(self.event_label, 1, 1, 1, 1)
        self.year_box = QtGui.QComboBox(self.gridLayoutWidget)
        self.year_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.year_box.setObjectName("year_box")
        self.year_box.addItem("")
        self.gridLayout.addWidget(self.year_box, 2, 0, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.buttonBox = QtGui.QPushButton(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(300, 160, 88, 28))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setUnderline(False)
        font.setBold(False)
        self.buttonBox.setFont(font)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        self.year_label.setText(QtGui.QApplication.translate("Dialog", "Year", None, QtGui.QApplication.UnicodeUTF8))
        self.event_label.setText(QtGui.QApplication.translate("Dialog", "Event", None, QtGui.QApplication.UnicodeUTF8))
        self.year_box.setItemText(0, QtGui.QApplication.translate("Dialog", "2015", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Welcome", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBox.setText(QtGui.QApplication.translate("Dialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))

