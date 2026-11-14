# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPlainTextEdit, QScrollArea,
    QSizePolicy, QSpinBox, QStatusBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1170, 839)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionOpen.setEnabled(False)
        icon = QIcon()
        iconThemeName = u"system-file-manager"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionOpen.setIcon(icon)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon1 = QIcon()
        iconThemeName = u"window-close"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionQuit.setIcon(icon1)
        self.actionMods = QAction(MainWindow)
        self.actionMods.setObjectName(u"actionMods")
        self.actionMods.setEnabled(False)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_search = QFrame(self.centralwidget)
        self.frame_search.setObjectName(u"frame_search")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_search.sizePolicy().hasHeightForWidth())
        self.frame_search.setSizePolicy(sizePolicy1)
        self.frame_search.setFrameShape(QFrame.NoFrame)
        self.frame_search.setFrameShadow(QFrame.Plain)
        self.gridLayout_9 = QGridLayout(self.frame_search)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.vis_cmap = QLabel(self.frame_search)
        self.vis_cmap.setObjectName(u"vis_cmap")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.vis_cmap.sizePolicy().hasHeightForWidth())
        self.vis_cmap.setSizePolicy(sizePolicy2)
        self.vis_cmap.setMinimumSize(QSize(0, 24))
        self.vis_cmap.setFrameShape(QFrame.Panel)
        self.vis_cmap.setFrameShadow(QFrame.Sunken)
        self.vis_cmap.setScaledContents(True)

        self.gridLayout_9.addWidget(self.vis_cmap, 2, 0, 1, 2)

        self.lineEdit_search = QLineEdit(self.frame_search)
        self.lineEdit_search.setObjectName(u"lineEdit_search")

        self.gridLayout_9.addWidget(self.lineEdit_search, 1, 1, 1, 1)

        self.lbl_search = QLabel(self.frame_search)
        self.lbl_search.setObjectName(u"lbl_search")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lbl_search.sizePolicy().hasHeightForWidth())
        self.lbl_search.setSizePolicy(sizePolicy3)

        self.gridLayout_9.addWidget(self.lbl_search, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_search, 2, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setLayoutDirection(Qt.LeftToRight)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setElideMode(Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(True)
        self.tab_engines = QWidget()
        self.tab_engines.setObjectName(u"tab_engines")
        self.gridLayout = QGridLayout(self.tab_engines)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tbl_engines = QTableWidget(self.tab_engines)
        self.tbl_engines.setObjectName(u"tbl_engines")
        self.tbl_engines.setAlternatingRowColors(True)
        self.tbl_engines.setCornerButtonEnabled(False)
        self.tbl_engines.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_engines.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.tbl_engines.verticalHeader().setProperty(u"showSortIndicator", False)

        self.gridLayout.addWidget(self.tbl_engines, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_engines, "")
        self.tab_wagons = QWidget()
        self.tab_wagons.setObjectName(u"tab_wagons")
        self.gridLayout_3 = QGridLayout(self.tab_wagons)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tbl_wagons = QTableWidget(self.tab_wagons)
        self.tbl_wagons.setObjectName(u"tbl_wagons")
        self.tbl_wagons.setAlternatingRowColors(True)
        self.tbl_wagons.setCornerButtonEnabled(False)
        self.tbl_wagons.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_wagons.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_3.addWidget(self.tbl_wagons, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_wagons, "")
        self.tab_vehicles = QWidget()
        self.tab_vehicles.setObjectName(u"tab_vehicles")
        self.gridLayout_4 = QGridLayout(self.tab_vehicles)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.tbl_vehicles = QTableWidget(self.tab_vehicles)
        self.tbl_vehicles.setObjectName(u"tbl_vehicles")
        self.tbl_vehicles.setAlternatingRowColors(True)
        self.tbl_vehicles.setCornerButtonEnabled(False)
        self.tbl_vehicles.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_vehicles.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_4.addWidget(self.tbl_vehicles, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_vehicles, "")
        self.tab_aircraft = QWidget()
        self.tab_aircraft.setObjectName(u"tab_aircraft")
        self.gridLayout_5 = QGridLayout(self.tab_aircraft)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.tbl_aircraft = QTableWidget(self.tab_aircraft)
        self.tbl_aircraft.setObjectName(u"tbl_aircraft")
        self.tbl_aircraft.setAlternatingRowColors(True)
        self.tbl_aircraft.setCornerButtonEnabled(False)
        self.tbl_aircraft.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_aircraft.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_5.addWidget(self.tbl_aircraft, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_aircraft, "")
        self.tab_all = QWidget()
        self.tab_all.setObjectName(u"tab_all")
        self.gridLayout_8 = QGridLayout(self.tab_all)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.tbl_all = QTableWidget(self.tab_all)
        self.tbl_all.setObjectName(u"tbl_all")
        self.tbl_all.setAlternatingRowColors(True)
        self.tbl_all.setCornerButtonEnabled(False)
        self.tbl_all.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_all.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_8.addWidget(self.tbl_all, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_all, "")
        self.tab_prefs = QWidget()
        self.tab_prefs.setObjectName(u"tab_prefs")
        self.verticalLayout = QVBoxLayout(self.tab_prefs)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.tab_prefs)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1170, 687))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy4)
        self.frame.setMinimumSize(QSize(16, 12))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_12 = QGridLayout(self.frame)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(0, 0, 0, 0)
        self.groupBox_display = QGroupBox(self.frame)
        self.groupBox_display.setObjectName(u"groupBox_display")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.groupBox_display.sizePolicy().hasHeightForWidth())
        self.groupBox_display.setSizePolicy(sizePolicy5)
        self.groupBox_display.setMaximumSize(QSize(16777215, 16777215))
        self.groupBox_display.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.groupBox_display.setFlat(True)
        self.groupBox_display.setCheckable(False)
        self.formLayout = QFormLayout(self.groupBox_display)
        self.formLayout.setObjectName(u"formLayout")
        self.label_unit = QLabel(self.groupBox_display)
        self.label_unit.setObjectName(u"label_unit")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_unit.sizePolicy().hasHeightForWidth())
        self.label_unit.setSizePolicy(sizePolicy6)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_unit)

        self.sel_unit = QComboBox(self.groupBox_display)
        self.sel_unit.addItem("")
        self.sel_unit.addItem("")
        self.sel_unit.setObjectName(u"sel_unit")
        sizePolicy4.setHeightForWidth(self.sel_unit.sizePolicy().hasHeightForWidth())
        self.sel_unit.setSizePolicy(sizePolicy4)
        self.sel_unit.setMinimumSize(QSize(60, 0))

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sel_unit)

        self.label_cmap = QLabel(self.groupBox_display)
        self.label_cmap.setObjectName(u"label_cmap")
        sizePolicy6.setHeightForWidth(self.label_cmap.sizePolicy().hasHeightForWidth())
        self.label_cmap.setSizePolicy(sizePolicy6)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_cmap)

        self.sel_cmap = QComboBox(self.groupBox_display)
        self.sel_cmap.addItem("")
        self.sel_cmap.setObjectName(u"sel_cmap")
        sizePolicy6.setHeightForWidth(self.sel_cmap.sizePolicy().hasHeightForWidth())
        self.sel_cmap.setSizePolicy(sizePolicy6)
        self.sel_cmap.setMinimumSize(QSize(60, 0))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.sel_cmap)

        self.label_3 = QLabel(self.groupBox_display)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.sel_cmap_inv = QCheckBox(self.groupBox_display)
        self.sel_cmap_inv.setObjectName(u"sel_cmap_inv")
        self.sel_cmap_inv.setEnabled(False)
        sizePolicy4.setHeightForWidth(self.sel_cmap_inv.sizePolicy().hasHeightForWidth())
        self.sel_cmap_inv.setSizePolicy(sizePolicy4)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.sel_cmap_inv)

        self.label_2 = QLabel(self.groupBox_display)
        self.label_2.setObjectName(u"label_2")
        sizePolicy4.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy4)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_2)


        self.gridLayout_12.addWidget(self.groupBox_display, 0, 0, 1, 1)

        self.groupBox_tokens = QGroupBox(self.frame)
        self.groupBox_tokens.setObjectName(u"groupBox_tokens")
        sizePolicy4.setHeightForWidth(self.groupBox_tokens.sizePolicy().hasHeightForWidth())
        self.groupBox_tokens.setSizePolicy(sizePolicy4)
        self.groupBox_tokens.setMinimumSize(QSize(300, 0))
        self.groupBox_tokens.setMaximumSize(QSize(16777215, 16777215))
        self.groupBox_tokens.setFlat(True)
        self.groupBox_tokens.setCheckable(False)
        self.gridLayout_6 = QGridLayout(self.groupBox_tokens)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setVerticalSpacing(6)
        self.gridLayout_6.setContentsMargins(-1, 9, -1, -1)
        self.lbl_adj_cash = QLabel(self.groupBox_tokens)
        self.lbl_adj_cash.setObjectName(u"lbl_adj_cash")
        sizePolicy6.setHeightForWidth(self.lbl_adj_cash.sizePolicy().hasHeightForWidth())
        self.lbl_adj_cash.setSizePolicy(sizePolicy6)
        self.lbl_adj_cash.setMinimumSize(QSize(30, 0))

        self.gridLayout_6.addWidget(self.lbl_adj_cash, 1, 2, 1, 1)

        self.lbl_cash = QLabel(self.groupBox_tokens)
        self.lbl_cash.setObjectName(u"lbl_cash")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.lbl_cash.sizePolicy().hasHeightForWidth())
        self.lbl_cash.setSizePolicy(sizePolicy7)

        self.gridLayout_6.addWidget(self.lbl_cash, 1, 0, 1, 1)

        self.amt_cash = QSpinBox(self.groupBox_tokens)
        self.amt_cash.setObjectName(u"amt_cash")
        sizePolicy6.setHeightForWidth(self.amt_cash.sizePolicy().hasHeightForWidth())
        self.amt_cash.setSizePolicy(sizePolicy6)
        self.amt_cash.setMinimumSize(QSize(50, 0))
        self.amt_cash.setFrame(True)
        self.amt_cash.setMaximum(10000)
        self.amt_cash.setSingleStep(10)
        self.amt_cash.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_cash.setValue(1000)

        self.gridLayout_6.addWidget(self.amt_cash, 1, 1, 1, 1)

        self.amt_coal = QSpinBox(self.groupBox_tokens)
        self.amt_coal.setObjectName(u"amt_coal")
        sizePolicy6.setHeightForWidth(self.amt_coal.sizePolicy().hasHeightForWidth())
        self.amt_coal.setSizePolicy(sizePolicy6)
        self.amt_coal.setMinimumSize(QSize(50, 0))
        self.amt_coal.setMaximum(10000)
        self.amt_coal.setSingleStep(10)
        self.amt_coal.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_coal.setValue(500)

        self.gridLayout_6.addWidget(self.amt_coal, 2, 1, 1, 1)

        self.lbl_coal = QLabel(self.groupBox_tokens)
        self.lbl_coal.setObjectName(u"lbl_coal")
        sizePolicy7.setHeightForWidth(self.lbl_coal.sizePolicy().hasHeightForWidth())
        self.lbl_coal.setSizePolicy(sizePolicy7)

        self.gridLayout_6.addWidget(self.lbl_coal, 2, 0, 1, 1)

        self.lbl_adj_coal = QLabel(self.groupBox_tokens)
        self.lbl_adj_coal.setObjectName(u"lbl_adj_coal")
        sizePolicy7.setHeightForWidth(self.lbl_adj_coal.sizePolicy().hasHeightForWidth())
        self.lbl_adj_coal.setSizePolicy(sizePolicy7)
        self.lbl_adj_coal.setMinimumSize(QSize(30, 0))

        self.gridLayout_6.addWidget(self.lbl_adj_coal, 2, 2, 1, 1)

        self.amt_diesel = QSpinBox(self.groupBox_tokens)
        self.amt_diesel.setObjectName(u"amt_diesel")
        sizePolicy6.setHeightForWidth(self.amt_diesel.sizePolicy().hasHeightForWidth())
        self.amt_diesel.setSizePolicy(sizePolicy6)
        self.amt_diesel.setMinimumSize(QSize(50, 0))
        self.amt_diesel.setMaximum(10000)
        self.amt_diesel.setSingleStep(10)
        self.amt_diesel.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_diesel.setValue(500)

        self.gridLayout_6.addWidget(self.amt_diesel, 3, 1, 1, 1)

        self.amt_electric = QSpinBox(self.groupBox_tokens)
        self.amt_electric.setObjectName(u"amt_electric")
        sizePolicy6.setHeightForWidth(self.amt_electric.sizePolicy().hasHeightForWidth())
        self.amt_electric.setSizePolicy(sizePolicy6)
        self.amt_electric.setMinimumSize(QSize(50, 0))
        self.amt_electric.setMaximum(10000)
        self.amt_electric.setSingleStep(10)
        self.amt_electric.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_electric.setValue(250)

        self.gridLayout_6.addWidget(self.amt_electric, 4, 1, 1, 1)

        self.lbl_diesel = QLabel(self.groupBox_tokens)
        self.lbl_diesel.setObjectName(u"lbl_diesel")
        sizePolicy7.setHeightForWidth(self.lbl_diesel.sizePolicy().hasHeightForWidth())
        self.lbl_diesel.setSizePolicy(sizePolicy7)

        self.gridLayout_6.addWidget(self.lbl_diesel, 3, 0, 1, 1)

        self.lbl_electric = QLabel(self.groupBox_tokens)
        self.lbl_electric.setObjectName(u"lbl_electric")
        sizePolicy6.setHeightForWidth(self.lbl_electric.sizePolicy().hasHeightForWidth())
        self.lbl_electric.setSizePolicy(sizePolicy6)
        self.lbl_electric.setMinimumSize(QSize(0, 0))

        self.gridLayout_6.addWidget(self.lbl_electric, 4, 0, 1, 1)

        self.lbl_adj_diesel = QLabel(self.groupBox_tokens)
        self.lbl_adj_diesel.setObjectName(u"lbl_adj_diesel")
        sizePolicy7.setHeightForWidth(self.lbl_adj_diesel.sizePolicy().hasHeightForWidth())
        self.lbl_adj_diesel.setSizePolicy(sizePolicy7)
        self.lbl_adj_diesel.setMinimumSize(QSize(30, 0))

        self.gridLayout_6.addWidget(self.lbl_adj_diesel, 3, 2, 1, 1)

        self.lbl_adj_electric = QLabel(self.groupBox_tokens)
        self.lbl_adj_electric.setObjectName(u"lbl_adj_electric")
        sizePolicy7.setHeightForWidth(self.lbl_adj_electric.sizePolicy().hasHeightForWidth())
        self.lbl_adj_electric.setSizePolicy(sizePolicy7)
        self.lbl_adj_electric.setMinimumSize(QSize(30, 0))

        self.gridLayout_6.addWidget(self.lbl_adj_electric, 4, 2, 1, 1)

        self.label = QLabel(self.groupBox_tokens)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(240, 0))
        self.label.setMaximumSize(QSize(500, 16777215))
        self.label.setFrameShape(QFrame.NoFrame)
        self.label.setFrameShadow(QFrame.Sunken)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setWordWrap(True)

        self.gridLayout_6.addWidget(self.label, 1, 4, 4, 3)

        self.line = QFrame(self.groupBox_tokens)
        self.line.setObjectName(u"line")
        sizePolicy5.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy5)
        self.line.setMinimumSize(QSize(0, 0))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_6.addWidget(self.line, 1, 3, 4, 1)


        self.gridLayout_12.addWidget(self.groupBox_tokens, 0, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.frame, 0, Qt.AlignTop)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(1)
        sizePolicy8.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy8)
        self.groupBox.setFlat(True)
        self.gridLayout_7 = QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.lbl_vfiles = QLabel(self.groupBox)
        self.lbl_vfiles.setObjectName(u"lbl_vfiles")

        self.gridLayout_7.addWidget(self.lbl_vfiles, 1, 0, 1, 1)

        self.txt_vfiles = QLineEdit(self.groupBox)
        self.txt_vfiles.setObjectName(u"txt_vfiles")
        self.txt_vfiles.setReadOnly(True)

        self.gridLayout_7.addWidget(self.txt_vfiles, 1, 1, 1, 1)

        self.lbl_moddir = QLabel(self.groupBox)
        self.lbl_moddir.setObjectName(u"lbl_moddir")

        self.gridLayout_7.addWidget(self.lbl_moddir, 3, 0, 1, 1)

        self.txt_vdir = QLineEdit(self.groupBox)
        self.txt_vdir.setObjectName(u"txt_vdir")
        self.txt_vdir.setReadOnly(True)

        self.gridLayout_7.addWidget(self.txt_vdir, 0, 1, 1, 1)

        self.lbl_others = QLabel(self.groupBox)
        self.lbl_others.setObjectName(u"lbl_others")

        self.gridLayout_7.addWidget(self.lbl_others, 6, 0, 1, 1)

        self.lbl_vdir = QLabel(self.groupBox)
        self.lbl_vdir.setObjectName(u"lbl_vdir")

        self.gridLayout_7.addWidget(self.lbl_vdir, 0, 0, 1, 1)

        self.txt_found_modfiles = QPlainTextEdit(self.groupBox)
        self.txt_found_modfiles.setObjectName(u"txt_found_modfiles")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(1)
        sizePolicy9.setHeightForWidth(self.txt_found_modfiles.sizePolicy().hasHeightForWidth())
        self.txt_found_modfiles.setSizePolicy(sizePolicy9)
        self.txt_found_modfiles.setTabChangesFocus(True)
        self.txt_found_modfiles.setReadOnly(True)

        self.gridLayout_7.addWidget(self.txt_found_modfiles, 7, 0, 1, 2)

        self.txt_modfiles = QLineEdit(self.groupBox)
        self.txt_modfiles.setObjectName(u"txt_modfiles")
        self.txt_modfiles.setReadOnly(True)

        self.gridLayout_7.addWidget(self.txt_modfiles, 6, 1, 1, 1)

        self.txt_moddir = QLineEdit(self.groupBox)
        self.txt_moddir.setObjectName(u"txt_moddir")
        self.txt_moddir.setReadOnly(True)

        self.gridLayout_7.addWidget(self.txt_moddir, 3, 1, 1, 1)

        self.txt_found_vfiles = QPlainTextEdit(self.groupBox)
        self.txt_found_vfiles.setObjectName(u"txt_found_vfiles")
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.txt_found_vfiles.sizePolicy().hasHeightForWidth())
        self.txt_found_vfiles.setSizePolicy(sizePolicy10)
        self.txt_found_vfiles.setMaximumSize(QSize(16777215, 64))
        self.txt_found_vfiles.setBaseSize(QSize(0, 24))
        self.txt_found_vfiles.setTabChangesFocus(True)
        self.txt_found_vfiles.setReadOnly(True)

        self.gridLayout_7.addWidget(self.txt_found_vfiles, 2, 0, 1, 2)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab_prefs, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1170, 22))
        self.menuFiles = QMenu(self.menubar)
        self.menuFiles.setObjectName(u"menuFiles")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFiles.menuAction())
        self.menuFiles.addAction(self.actionOpen)
        self.menuFiles.addAction(self.actionMods)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionQuit)

        self.retranslateUi(MainWindow)
        self.actionQuit.triggered.connect(MainWindow.close)
        self.actionOpen.triggered.connect(MainWindow.open)
        self.actionMods.triggered.connect(MainWindow.open)
        self.amt_coal.valueChanged.connect(MainWindow.set_coal)
        self.sel_unit.currentIndexChanged.connect(MainWindow.set_disp_unit)
        self.amt_cash.valueChanged.connect(MainWindow.set_cash)
        self.amt_diesel.valueChanged.connect(MainWindow.set_diesel)
        self.sel_cmap.currentTextChanged.connect(MainWindow.set_disp_cmap)
        self.amt_electric.valueChanged.connect(MainWindow.set_electric)
        self.tabWidget.currentChanged.connect(MainWindow.update_table)
        self.sel_cmap_inv.stateChanged.connect(MainWindow.set_disp_cmap_inv)

        self.tabWidget.setCurrentIndex(5)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mashinky Stats Viewer", None))
        MainWindow.setProperty(u"ModDir", "")
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open Files...", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+W", None))
#endif // QT_CONFIG(shortcut)
        self.actionMods.setText(QCoreApplication.translate("MainWindow", u"Open Mods Folder...", None))
#if QT_CONFIG(shortcut)
        self.actionMods.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+M", None))
#endif // QT_CONFIG(shortcut)
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.vis_cmap.setText("")
        self.lbl_search.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_engines), QCoreApplication.translate("MainWindow", u"Engines", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_wagons), QCoreApplication.translate("MainWindow", u"Wagons", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_vehicles), QCoreApplication.translate("MainWindow", u"Vehicles", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_aircraft), QCoreApplication.translate("MainWindow", u"Aircraft", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_all), QCoreApplication.translate("MainWindow", u"All", None))
        self.groupBox_display.setTitle(QCoreApplication.translate("MainWindow", u"Display configuration", None))
        self.label_unit.setText(QCoreApplication.translate("MainWindow", u"Speed unit", None))
        self.sel_unit.setItemText(0, QCoreApplication.translate("MainWindow", u"kmph", None))
        self.sel_unit.setItemText(1, QCoreApplication.translate("MainWindow", u"mph", None))

        self.label_cmap.setText(QCoreApplication.translate("MainWindow", u"Colormap", None))
        self.sel_cmap.setItemText(0, QCoreApplication.translate("MainWindow", u"None", None))

        self.label_3.setText("")
        self.sel_cmap_inv.setText(QCoreApplication.translate("MainWindow", u"Invert", None))
        self.label_2.setText("")
        self.groupBox_tokens.setTitle(QCoreApplication.translate("MainWindow", u"Token Budgets", None))
        self.lbl_adj_cash.setText(QCoreApplication.translate("MainWindow", u"1.0", None))
        self.lbl_cash.setText(QCoreApplication.translate("MainWindow", u"Money", None))
        self.lbl_coal.setText(QCoreApplication.translate("MainWindow", u"Coal", None))
        self.lbl_adj_coal.setText(QCoreApplication.translate("MainWindow", u"10.00", None))
        self.lbl_diesel.setText(QCoreApplication.translate("MainWindow", u"Diesel", None))
        self.lbl_electric.setText(QCoreApplication.translate("MainWindow", u"Electricity", None))
        self.lbl_adj_diesel.setText(QCoreApplication.translate("MainWindow", u"10.00", None))
        self.lbl_adj_electric.setText(QCoreApplication.translate("MainWindow", u"10.00", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"These inputs are used to configure the \"Adjusted Cost\" values assigned to each token type, which is the reciprocal of the token budget divided by the reciprocal of the \"money\" token value, such that the normalized value of a money token is always 1. The calculated value is displayed underneath each box.", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Files", None))
        self.lbl_vfiles.setText(QCoreApplication.translate("MainWindow", u"Vanilla files", None))
        self.lbl_moddir.setText(QCoreApplication.translate("MainWindow", u"Mod dirs", None))
        self.lbl_others.setText(QCoreApplication.translate("MainWindow", u"Mod files", None))
        self.lbl_vdir.setText(QCoreApplication.translate("MainWindow", u"Vanilla dirs", None))
#if QT_CONFIG(tooltip)
        self.txt_found_modfiles.setToolTip(QCoreApplication.translate("MainWindow", u"All found mod .xml files", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.txt_found_vfiles.setToolTip(QCoreApplication.translate("MainWindow", u"All found vanilla .xml files", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_prefs), QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.menuFiles.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

